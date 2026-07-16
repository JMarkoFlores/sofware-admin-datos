"""
Blueprint del módulo Disparador.
Se conecta a Bibliouni vía db_tenebrosa.py y whatsapp.py.

Extensiones incluidas:
- Disparador de mensajes (INTACTO)
- Monitoreo de backup diario a las 7:00 AM (America/Lima)
- Webhook para recepción de comandos vía Evolution API
- Reportes interactivos por WhatsApp con menús dinámicos
- Reportes automáticos diarios y semanales
"""

import os
import requests
from datetime import datetime
from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from db_tenebrosa import get_tables_info
from whatsapp import send_document, send_message, format_tables_message
from utils.helpers import log_auditoria
from services.backup_service import (
    verificar_backup_hoy,
    enviar_alerta_backup_pendiente,
    procesar_comando_backup,
)
from services.fill_factor_service import (
    procesar_comando_fill_factor,
    verificar_fragmentacion,
    enviar_alerta_fragmentacion,
    enviar_ok_fragmentacion,
)
from models.user_conversation import UserConversation

from services.interactive_reports_service import (
    generar_menu_principal,
    procesar_mensaje_usuario,
    generar_y_enviar_reporte,
    actualizar_estado_reporte_enviado,
    obtener_estado_conversacion,
    REPORT_TYPES,
from services.login_security_service import (
    check_failed_attempts,
    procesar_comando_login,
)
from config.settings import Config

bp = Blueprint('disparador', __name__)

# ---------------------------------------------------------------------------
# Estado global del disparador de MENSAJES (INTACTO)
# ---------------------------------------------------------------------------
is_running = False
last_sent = None
last_message = None
current_destination = os.getenv('WHATSAPP_DESTINATION', '51900685850')
scheduler = BackgroundScheduler()
scheduler.start()

INTERVAL_MINUTES = 1

# ---------------------------------------------------------------------------
# Estado global del disparador de BACKUP (NUEVO)
# ---------------------------------------------------------------------------
backup_is_running = False
backup_last_check = None
backup_last_result = None
backup_destination = os.getenv('WHATSAPP_DESTINATION', '51900685850')
BACKUP_CHECK_HOUR = int(os.getenv('BACKUP_CHECK_HOUR', '7'))
BACKUP_CHECK_MINUTE = int(os.getenv('BACKUP_CHECK_MINUTE', '0'))
BACKUP_TIMEZONE = os.getenv('BACKUP_TIMEZONE', 'America/Lima')
WEBHOOK_URL = os.getenv(
    'WEBHOOK_URL',
    'http://host.docker.internal:5000/api/backup/webhook'
)
_flask_app = None  # Referencia a la app Flask para app_context en jobs

# ---------------------------------------------------------------------------
# Estado global del monitoreo de FRAGMENTACIÓN
# ---------------------------------------------------------------------------
frag_is_running = False
frag_last_check = None
frag_last_result = None
frag_umbral = int(os.getenv('FRAG_UMBRAL', '30'))
FRAG_INTERVAL_MINUTES = int(os.getenv('FRAG_INTERVAL_MINUTES', '60'))

# ---------------------------------------------------------------------------
# Estado global del monitoreo de SEGURIDAD DE LOGIN
# ---------------------------------------------------------------------------
login_security_is_running = False
login_security_last_check = None
login_security_last_alert = None  # Nueva variable para la última alerta
login_security_destination = os.getenv('WHATSAPP_DESTINATION', '5190065850')
LOGIN_CHECK_INTERVAL_MINUTES = int(os.getenv('LOGIN_CHECK_INTERVAL_MINUTES', '5'))


def set_flask_app(app):
    """Recibe la instancia de Flask para poder usar app_context en jobs."""
    global _flask_app
    _flask_app = app


# ---------------------------------------------------------------------------
# Estado global de REPORTES AUTOMÁTICOS (NUEVO)
# =====================
# ESTADO GLOBAL REPORTES AUTOMÁTICOS
# =====================
reports_is_running = False
reports_last_daily = None
reports_last_weekly = None
reports_last_monthly = None
reports_destination = os.getenv('WHATSAPP_DESTINATION', '51900685850')

# Habilitación de reportes
reports_daily_enabled = True
reports_weekly_enabled = True
reports_monthly_enabled = True

# VALORES POR DEFECTO (pueden ser sobrescritos dinámicamente)
REPORTS_DAILY_HOUR = int(os.getenv('REPORTS_DAILY_HOUR', '8'))
REPORTS_DAILY_MINUTE = int(os.getenv('REPORTS_DAILY_MINUTE', '0'))
REPORTS_WEEKLY_DAY = os.getenv('REPORTS_WEEKLY_DAY', 'MON')  # MON, TUE, WED, etc.
REPORTS_WEEKLY_HOUR = int(os.getenv('REPORTS_WEEKLY_HOUR', '9'))
REPORTS_WEEKLY_MINUTE = int(os.getenv('REPORTS_WEEKLY_MINUTE', '0'))
REPORTS_MONTHLY_DAY = int(os.getenv('REPORTS_MONTHLY_DAY', '1'))
REPORTS_MONTHLY_HOUR = int(os.getenv('REPORTS_MONTHLY_HOUR', '10'))
REPORTS_MONTHLY_MINUTE = int(os.getenv('REPORTS_MONTHLY_MINUTE', '0'))
REPORTS_TIMEZONE = os.getenv('REPORTS_TIMEZONE', 'America/Lima')
REPORTS_DAILY_TYPES = os.getenv('REPORTS_DAILY_TYPES', 'estadisticas,multas').split(',')
REPORTS_WEEKLY_TYPES = os.getenv('REPORTS_WEEKLY_TYPES', 'estadisticas,libros_prestados,devoluciones_pendientes').split(',')
REPORTS_MONTHLY_TYPES = os.getenv('REPORTS_MONTHLY_TYPES', 'estadisticas,libros_prestados,multas').split(',')


def send_menu_scheduled(periodo):
    """Envía el menú interactivo en la hora programada (para daily/weekly/monthly)."""
    print(f"[{datetime.now()}] Enviando menú {periodo} a {reports_destination}...")
    
    with _flask_app.app_context():
        menu_message = generar_menu_principal()
        send_result = send_message(menu_message, reports_destination)
        if send_result.get('success'):
            UserConversation.get_or_create(reports_destination).update_state('menu')
            print(f"[OK] Menú {periodo} enviado a {reports_destination}")
            log_auditoria(
                'REPORTE_AUTOMÁTICO',
                'WhatsApp',
                f'Menú {periodo} enviado',
                usuario='sistema',
                resultado='Éxito',
                detalle=f'Destino: {reports_destination}'
            )
        else:
            print(f"[ERROR] Fallo al enviar menú {periodo}")
            log_auditoria(
                'REPORTE_AUTOMÁTICO',
                'WhatsApp',
                f'Fallo al enviar menú {periodo}',
                usuario='sistema',
                resultado='Fallo',
                detalle=f'Error: {send_result.get("error", "Unknown")}'
            )


def execute_daily_report():
    """Envía el menú interactivo diario en la hora programada."""
    global reports_last_daily
    if not _flask_app:
        print(f"[ERROR] Flask app no disponible para reporte diario")
        return
    reports_last_daily = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_menu_scheduled("diario")


def execute_weekly_report():
    """Envía el menú interactivo semanal en la hora programada."""
    global reports_last_weekly
    if not _flask_app:
        print(f"[ERROR] Flask app no disponible para reporte semanal")
        return
    reports_last_weekly = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_menu_scheduled("semanal")


def execute_monthly_report():
    """Envía el menú interactivo mensual en la hora programada."""
    global reports_last_monthly
    if not _flask_app:
        print(f"[ERROR] Flask app no disponible para reporte mensual")
        return
    reports_last_monthly = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_menu_scheduled("mensual")


def validate_phone(number):
    """Valida que el número tenga formato correcto."""
    if not number:
        return False, "El número no puede estar vacío"
    cleaned = number.replace(' ', '').replace('+', '')
    if not cleaned.isdigit():
        return False, "El número solo debe contener dígitos"
    if len(cleaned) < 10:
        return False, f"El número es muy corto ({len(cleaned)} dígitos). Mínimo 10."
    if len(cleaned) > 13:
        return False, f"El número es muy largo ({len(cleaned)} dígitos). Máximo 13."
    return True, cleaned


# ===========================================================================
# DISPARADOR DE MENSAJES (INTACTO)
# ===========================================================================

def execute_send():
    """Función periódica: consulta tablas y envía WhatsApp."""
    global last_sent, last_message
    print(f"[{datetime.now()}] Ejecutando envío programado a {current_destination}...")
    tables_info = get_tables_info()
    if 'error' in tables_info:
        print(f"[ERROR] No se pudo obtener tablas: {tables_info['error']}")
        last_message = f"Error: {tables_info['error']}"
        return
    message = format_tables_message(tables_info)
    result = send_message(message, current_destination)
    if result['success']:
        last_sent = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last_message = message[:100] + "..." if len(message) > 100 else message
        print(f"[OK] Mensaje enviado a {current_destination} a las {last_sent}")
    else:
        error_msg = result.get('error', f"Status {result.get('status_code', 'unknown')}")
        last_message = f"Error al enviar: {error_msg}"
        print(f"[ERROR] {last_message}")


def scheduled_execute_send():
    """Wrapper para ejecutar execute_send dentro del app_context de Flask."""
    if _flask_app:
        with _flask_app.app_context():
            execute_send()
    else:
        execute_send()


@bp.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@bp.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'is_running': is_running,
        'last_sent': last_sent,
        'last_message': last_message,
        'destination': current_destination,
        'interval_minutes': INTERVAL_MINUTES
    })


@bp.route('/api/test-send', methods=['GET'])
def test_send():
    print(f"[{datetime.now()}] TEST-SEND: Enviando mensaje de prueba a {current_destination}...")
    tables_info = get_tables_info()
    message = format_tables_message(tables_info)
    result = send_message(message, current_destination)
    print(f"[{datetime.now()}] TEST-SEND Resultado: {result}")
    return jsonify({
        'success': result['success'],
        'result': result,
        'message_sent': message[:200] if len(message) > 200 else message
    })


@bp.route('/api/start', methods=['POST'])
def start_scheduler():
    global is_running, current_destination
    if is_running:
        return jsonify({'success': False, 'message': 'El disparador ya está activo'})
    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    if not phone_number:
        return jsonify({'success': False, 'message': 'Debes proporcionar un número de teléfono'}), 400
    is_valid, result = validate_phone(phone_number)
    if not is_valid:
        return jsonify({'success': False, 'message': result}), 400
    current_destination = result
    print(f"[{datetime.now()}] Número actualizado: {current_destination}")

    scheduler.add_job(
        scheduled_execute_send,
        'interval',
        minutes=INTERVAL_MINUTES,
        id='whatsapp_disparo',
        replace_existing=True
    )
    is_running = True

    # Enviar el primer mensaje de inmediato al presionar Iniciar
    print(f"[{datetime.now()}] Enviando mensaje inicial inmediato a {current_destination}...")
    execute_send()

    return jsonify({
        'success': True,
        'message': f'Disparador iniciado para el número {current_destination}',
        'destination': current_destination,
        'last_sent': last_sent,
        'last_message': last_message
    })


@bp.route('/api/stop', methods=['GET'])
def stop_scheduler():
    global is_running
    if not is_running:
        return jsonify({'success': False, 'message': 'El disparo no está activo'})
    scheduler.remove_job('whatsapp_disparo')
    is_running = False
    return jsonify({'success': True, 'message': 'Disparo detenido'})


@bp.route('/api/tables', methods=['GET'])
def get_tables():
    tables_info = get_tables_info()
    return jsonify(tables_info)


# ===========================================================================
# MONITOREO DE BACKUP (NUEVO)
# ===========================================================================

def configure_evolution_webhook():
    """
    Configura automáticamente el webhook en Evolution API para recibir
    mensajes entrantes en /api/backup/webhook.
    """
    url = f"{Config.EVOLUTION_URL}/webhook/set/{Config.EVOLUTION_INSTANCE}"
    headers = {
        'apikey': Config.EVOLUTION_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'webhook': {
            'enabled': True,
            'url': WEBHOOK_URL,
            'webhook_by_events': False,
            'webhook_base64': False,
            'events': ['MESSAGES_UPSERT']
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            print(f"[OK] Webhook configurado en Evolution: {WEBHOOK_URL}")
            return True
        else:
            print(f"[WARN] No se pudo configurar webhook. Status: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Excepción al configurar webhook: {e}")
        return False


def _check_backup_daily_impl():
    """Implementación interna de la verificación de backup."""
    global backup_last_check, backup_last_result

    print(f"[{datetime.now()}] Verificando backup diario de Bibliouni...")
    backup_last_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    resultado = verificar_backup_hoy()

    if resultado['existe']:
        backup_last_result = 'exito'
        log_auditoria(
            'VERIFICACIÓN',
            'Backup',
            resultado['detalle'],
            usuario='sistema',
            resultado='Éxito'
        )
        print(f"[OK] {resultado['detalle']}")
    else:
        log_auditoria(
            'ALERTA',
            'Backup',
            resultado['detalle'],
            usuario='sistema',
            resultado='Fallo'
        )
        print(f"[ALERTA] {resultado['detalle']}")
        print(f"[INFO] Enviando alerta de backup a {backup_destination}...")

        send_result = enviar_alerta_backup_pendiente(backup_destination)

        if send_result.get('success'):
            backup_last_result = 'alerta'
            print(f"[OK] Alerta de backup enviada correctamente a {backup_destination}")
        else:
            backup_last_result = 'alerta_error_envio'
            error_detail = send_result.get('error') or f"Status {send_result.get('status_code', 'unknown')}"
            print(f"[ERROR] No se pudo enviar alerta de backup: {error_detail}")
            print(f"[DEBUG] Respuesta completa de Evolution: {send_result}")
            log_auditoria(
                'ERROR',
                'Backup',
                f'Fallo al enviar alerta WhatsApp: {error_detail}',
                usuario='sistema',
                resultado='Fallo',
                detalle=str(send_result)
            )


def check_backup_daily():
    """
    Función ejecutada diariamente por APScheduler.
    Verifica backup de hoy y alerta vía WhatsApp si no existe.
    Se ejecuta dentro de un Flask app_context para que SQLAlchemy funcione.
    """
    if _flask_app:
        with _flask_app.app_context():
            _check_backup_daily_impl()
    else:
        print("[ERROR] No se ha configurado la app Flask. No se puede ejecutar check_backup_daily.")


@bp.route('/api/backup/start', methods=['POST'])
def start_backup_scheduler():
    """Inicia el monitoreo de backup (requiere número explícito)."""
    global backup_is_running, backup_destination

    if backup_is_running:
        return jsonify({'success': False, 'message': 'El monitoreo de backup ya está activo'})

    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    if not phone_number:
        return jsonify({'success': False, 'message': 'Debes proporcionar un número de teléfono'}), 400
    is_valid, result = validate_phone(phone_number)
    if not is_valid:
        return jsonify({'success': False, 'message': result}), 400
    backup_destination = result
    print(f"[{datetime.now()}] Número de backup actualizado: {backup_destination}")

    # Configurar webhook automáticamente en Evolution
    configure_evolution_webhook()

    # Programar verificación diaria a las 7:00 AM (America/Lima)
    scheduler.add_job(
        check_backup_daily,
        trigger=CronTrigger(
            hour=BACKUP_CHECK_HOUR,
            minute=BACKUP_CHECK_MINUTE,
            timezone=BACKUP_TIMEZONE
        ),
        id='backup_check',
        replace_existing=True
    )

    backup_is_running = True
    return jsonify({
        'success': True,
        'message': f'Monitoreo de backup iniciado para el número {backup_destination}',
        'destination': backup_destination,
        'next_run': str(scheduler.get_job('backup_check').next_run_time) if scheduler.get_job('backup_check') else None
    })


@bp.route('/api/backup/stop', methods=['GET'])
def stop_backup_scheduler():
    """Detiene el monitoreo de backup."""
    global backup_is_running
    if not backup_is_running:
        return jsonify({'success': False, 'message': 'El monitoreo de backup no está activo'})
    try:
        scheduler.remove_job('backup_check')
    except Exception:
        pass
    backup_is_running = False
    return jsonify({'success': True, 'message': 'Monitoreo de backup detenido'})


@bp.route('/api/backup/status', methods=['GET'])
def backup_status():
    """Devuelve el estado actual del monitoreo de backup."""
    job = scheduler.get_job('backup_check')
    next_run = str(job.next_run_time) if job else None
    return jsonify({
        'is_running': backup_is_running,
        'destination': backup_destination,
        'last_check': backup_last_check,
        'last_result': backup_last_result,
        'check_time': f'{BACKUP_CHECK_HOUR:02d}:{BACKUP_CHECK_MINUTE:02d}',
        'timezone': BACKUP_TIMEZONE,
        'next_run': next_run
    })


@bp.route('/api/backup/test-alert', methods=['GET'])
def test_backup_alert():
    """
    Endpoint de prueba: envía la alerta de backup pendiente de inmediato
    al número configurado, sin esperar al cron.
    """
    print(f"[{datetime.now()}] TEST-ALERT: Enviando alerta de backup a {backup_destination}...")
    send_result = enviar_alerta_backup_pendiente(backup_destination)
    print(f"[{datetime.now()}] TEST-ALERT Resultado: {send_result}")
    return jsonify({
        'success': send_result.get('success'),
        'destination': backup_destination,
        'result': send_result,
        'message_preview': (
            "🚨 ALERTA DE RESPALDO\\n\\nSistema: Bibliouni\\n\\n"
            "No se detectó un backup realizado el día de hoy.\\n\\n"
            "Estado:\\n❌ Backup pendiente\\n\\n"
            "Para resolver automáticamente responda:\\n\\nRESUELVE BACKUP"
        )
    })


@bp.route('/api/backup/test-check', methods=['GET'])
def test_backup_check():
    """
    Endpoint de prueba: ejecuta la verificación de backup manualmente
    (simula lo que haría el cron diario) para validar el flujo completo.
    """
    print(f"[{datetime.now()}] TEST-CHECK: Ejecutando verificación de backup manualmente...")
    check_backup_daily()
    return jsonify({
        'success': True,
        'message': 'Verificación de backup ejecutada manualmente. Revisa la consola de Flask y tu WhatsApp.',
        'last_check': backup_last_check,
        'last_result': backup_last_result,
        'destination': backup_destination
    })


def _extract_text_from_webhook_message(message):
    """Extrae texto de diferentes estructuras de mensaje de Evolution API."""
    if not isinstance(message, dict):
        return ''

    # Texto directo en la conversación
    if message.get('conversation'):
        return message.get('conversation', '').strip()

    # Mensaje extendido con texto opcional
    extended = message.get('extendedTextMessage') or {}
    if isinstance(extended, dict):
        text = extended.get('text', '') or extended.get('contextInfo', {}).get('quotedMessage', {}).get('conversation', '')
        if text:
            return text.strip()

    # Mensajes con caption (imagen, video, documento)
    for media_key in ['imageMessage', 'videoMessage']:
        media = message.get(media_key) or {}
        if isinstance(media, dict) and media.get('caption'):
            return media['caption'].strip()

    document_caption = (
        message.get('documentWithCaptionMessage', {})
        .get('message', {})
        .get('documentMessage', {})
        .get('caption', '')
    )
    if document_caption:
        return document_caption.strip()

    # Respuesta de botones
    buttons_response = message.get('buttonsResponseMessage') or {}
    if isinstance(buttons_response, dict):
        text = buttons_response.get('selectedButtonId') or buttons_response.get('selectedDisplayText')
        if text:
            return text.strip()

    # Respuesta de lista
    list_response = message.get('listResponseMessage') or {}
    if isinstance(list_response, dict):
        text = (
            list_response.get('title') or
            list_response.get('singleSelectReply', {}).get('selectedRowId')
        )
        if text:
            return text.strip()

    # Template button reply
    template_reply = message.get('templateButtonReplyMessage') or {}
    if isinstance(template_reply, dict):
        text = template_reply.get('selectedId') or template_reply.get('selectedDisplayText')
        if text:
            return text.strip()

    # Fallback: buscar cualquier campo string dentro del mensaje
    for key, value in message.items():
        if isinstance(value, str) and value.strip():
            return value.strip()

    return ''


@bp.route('/api/backup/webhook', methods=['POST'])
def backup_webhook():
    """
    Recibe mensajes entrantes de Evolution API.
    Procesa los siguientes comandos:
    - RESUELVE BACKUP: ejecuta un backup manual de Bibliouni.
    - FACTOR LLENADO <N>: reconstruye índices con el fill factor indicado.
    - BLOQUEA <username>: deshabilita un login de SQL Server.
    """
    payload = request.get_json() or {}

    # Log completo del payload para diagnóstico
    import json
    print(f"[DEBUG Webhook] Payload completo:\n{json.dumps(payload, indent=2, default=str)}")

    # Extraer datos del payload de Evolution API v2
    data = payload.get('data', {})
    key = data.get('key', {})
    message = data.get('message', {})

    remote_jid = key.get('remoteJid', '')
    from_me = key.get('fromMe', True)
    text = _extract_text_from_webhook_message(message)

    # Limpiar número: quitar @s.whatsapp.net, sufijos :1/:2 de dispositivos,
    # y dejar solo dígitos.
    numero_remoto = remote_jid.split('@')[0] if remote_jid else ''
    numero_remoto = numero_remoto.split(':')[0]
    numero_remoto = ''.join(c for c in numero_remoto if c.isdigit())

    print(f"[DEBUG Webhook] Mensaje entrante - remoteJid: {remote_jid}, "
          f"numero limpio: {numero_remoto}, fromMe: {from_me}, texto: '{text}'")

    # Ignorar mensajes: propios, sin texto, de grupos (@g.us) o sin número
    if from_me or not text or not numero_remoto or '@g.us' in remote_jid:
        print(f"[DEBUG Webhook] Mensaje ignorado - fromMe:{from_me}, texto:'{text}', "
              f"numero:{numero_remoto}, esGrupo:{'@g.us' in remote_jid}")
        return jsonify({'processed': False, 'reason': 'Ignored'}), 200

    log_auditoria(
        'WHATSAPP',
        'WhatsApp',
        'Mensaje recibido por webhook de WhatsApp',
        usuario='sistema',
        resultado='Éxito',
        detalle=f'Número: {numero_remoto}; Texto: {text[:160]}'
    )

    texto_upper = text.strip().upper()

    # Ejecutar procesamiento dentro de app_context para que
    # log_auditoria y db.session funcionen correctamente.
    # Solo se procesa UNA VEZ para evitar doble ejecución de comandos.
    
    
    ###Aqui empezó el conflicto (de mi parte)
    # def _procesar():
    #     if texto_upper.startswith('FACTOR LLENADO'):
    #         return procesar_comando_fill_factor(text, numero_remoto, backup_destination)
    # # log_auditoria y db.session funcionen correctamente
    
    # ###Aqui empezó el conflicto (de la parte de anthony)
    # if texto_upper.startswith('FACTOR LLENADO'):
    #     # Comando de fill factor: FACTOR LLENADO <porcentaje>
    #     if _flask_app:
    #         with _flask_app.app_context():
    #             resultado = procesar_comando_fill_factor(text, numero_remoto, backup_destination)
    #     else:
    #         print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
    #         resultado = procesar_comando_fill_factor(text, numero_remoto, backup_destination)
    # elif texto_upper.startswith('BLOQUEA'):
    #     # Comando de seguridad de login: BLOQUEA <username>
    #     if _flask_app:
    #         with _flask_app.app_context():
    #             resultado = procesar_comando_login(text, numero_remoto, login_security_destination)
    #     else:
    #         print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
    #         resultado = procesar_comando_login(text, numero_remoto, login_security_destination)
    # else:
    #     # Comando de backup: RESUELVE BACKUP (u otros futuros)
    #     if _flask_app:
    #         with _flask_app.app_context():
    #             resultado = procesar_comando_backup(text, numero_remoto, backup_destination)
    #     else:
    #         print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
    #         resultado = procesar_comando_backup(text, numero_remoto, backup_destination)

    #     # Primero intentar comando de backup
    #     resultado = procesar_comando_backup(text, numero_remoto, backup_destination)

    #     # Si no fue un comando de backup, intentar reporte interactivo
    #     if not resultado.get('processed', False):
    #         resultado_reporte = procesar_mensaje_reporte(text, numero_remoto)
    #         if resultado_reporte.get('processed'):
    #             return resultado_reporte

    #     return resultado
###
    def _procesar():
        
        if texto_upper.startswith('FACTOR LLENADO'):
            return procesar_comando_fill_factor(
                text,
                numero_remoto,
                backup_destination
            )

        elif texto_upper.startswith('BLOQUEA'):
            return procesar_comando_login(
                text,
                numero_remoto,
                login_security_destination
            )

        # Primero intentar comando de backup
        resultado = procesar_comando_backup(
            text,
            numero_remoto,
            backup_destination
        )

        # Si no fue backup, intentar reportes
        if not resultado.get("processed", False):
            resultado_reporte = procesar_mensaje_reporte(
                text,
                numero_remoto
            )

            if resultado_reporte.get("processed"):
                return resultado_reporte

        return resultado

    if _flask_app:
        with _flask_app.app_context():
            resultado = _procesar()
    else:
        print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
        resultado = _procesar()

    print(f"[DEBUG Webhook] Resultado del procesamiento: {resultado}")
    return jsonify(resultado), 200


@bp.route('/api/reports/simulate-incoming', methods=['POST'])
def simulate_incoming_message():
    """
    Endpoint de prueba: simula un mensaje entrante de WhatsApp para probar
    el flujo de reportes interactivos sin depender de Evolution API.
    """
    data = request.get_json() or {}
    numero = str(data.get('number', '')).strip()
    texto = str(data.get('text', '')).strip()

    if not numero or not texto:
        return jsonify({'success': False, 'message': 'Debes enviar number y text'}), 400

    print(f"[DEBUG Simulate] Simulando mensaje de {numero}: '{texto}'")

    def _procesar():
        resultado_backup = procesar_comando_backup(texto, numero, backup_destination)
        if resultado_backup.get('processed'):
            return resultado_backup
        return procesar_mensaje_reporte(texto, numero)

    if _flask_app:
        with _flask_app.app_context():
            resultado = _procesar()
    else:
        resultado = _procesar()

    return jsonify({
        'success': True,
        'number': numero,
        'text': texto,
        'result': resultado
    }), 200


# ===========================================================================
# FACTOR DE LLENADO - ENDPOINT DE PRUEBA
# ===========================================================================

@bp.route('/api/fill-factor/test', methods=['GET'])
def test_fill_factor():
    """
    Endpoint de prueba: ejecuta el rebuild de índices con el fill factor
    indicado como query parameter, sin necesidad de enviar WhatsApp.

    Query params:
        fill_factor (int): Porcentaje de llenado (1-100). Default: 80.
    """
    try:
        fill_factor = int(request.args.get('fill_factor', 80))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'fill_factor debe ser un número entero'}), 400

    if not (1 <= fill_factor <= 100):
        return jsonify({'success': False, 'message': f'fill_factor debe estar entre 1 y 100, recibido: {fill_factor}'}), 400

    print(f"[{datetime.now()}] TEST FILL FACTOR: ejecutando rebuild con FILLFACTOR={fill_factor}...")

    if _flask_app:
        with _flask_app.app_context():
            resultado = procesar_comando_fill_factor(
                f'FACTOR LLENADO {fill_factor}',
                backup_destination,
                backup_destination
            )
    else:
        resultado = procesar_comando_fill_factor(
            f'FACTOR LLENADO {fill_factor}',
            backup_destination,
            backup_destination
        )

    print(f"[{datetime.now()}] TEST FILL FACTOR Resultado: {resultado}")
    return jsonify({
        'success': resultado.get('exito', False),
        'fill_factor': fill_factor,
        'result': resultado
    })


# ===========================================================================
# MONITOREO DE FRAGMENTACIÓN DE ÍNDICES
# ===========================================================================

def _check_fragmentation_impl():
    """Implementación interna de la verificación de fragmentación."""
    global frag_last_check, frag_last_result

    print(f"[{datetime.now()}] Verificando fragmentación de índices en Bibliouni...")
    frag_last_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    resultado = verificar_fragmentacion(frag_umbral)
    frag_last_result = resultado

    if resultado['hay_alerta']:
        log_auditoria(
            'ALERTA',
            'Fragmentación',
            resultado['mensaje'],
            usuario='sistema',
            resultado='Alerta'
        )
        print(f"[ALERTA] {resultado['mensaje']}")
        enviar_alerta_fragmentacion(backup_destination, resultado)
    else:
        log_auditoria(
            'VERIFICACIÓN',
            'Fragmentación',
            resultado['mensaje'],
            usuario='sistema',
            resultado='Éxito'
        )
        print(f"[OK] {resultado['mensaje']}")


def check_fragmentation_daily():
    """Función ejecutada por APScheduler dentro de Flask app_context."""
    if _flask_app:
        with _flask_app.app_context():
            _check_fragmentation_impl()
    else:
        print("[ERROR] No se ha configurado la app Flask.")


@bp.route('/api/fragmentacion/start', methods=['POST'])
def start_frag_scheduler():
    """Inicia el monitoreo de fragmentación (programado diariamente)."""
    global frag_is_running, frag_umbral

    if frag_is_running:
        return jsonify({'success': False, 'message': 'El monitoreo de fragmentación ya está activo'})

    data = request.get_json() or {}
    umbral = data.get('umbral')
    if umbral is not None:
        try:
            umbral = int(umbral)
            if 1 <= umbral <= 100:
                frag_umbral = umbral
            else:
                return jsonify({'success': False, 'message': 'El umbral debe estar entre 1 y 100'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'El umbral debe ser un número entero'}), 400

    scheduler.add_job(
        check_fragmentation_daily,
        'interval',
        minutes=FRAG_INTERVAL_MINUTES,
        id='frag_check',
        replace_existing=True
    )

    frag_is_running = True
    return jsonify({
        'success': True,
        'message': f'Monitoreo de fragmentación iniciado. Verificación cada {FRAG_INTERVAL_MINUTES} minutos. Umbral: {frag_umbral}%.',
        'umbral': frag_umbral,
        'interval_minutes': FRAG_INTERVAL_MINUTES,
        'next_run': str(scheduler.get_job('frag_check').next_run_time) if scheduler.get_job('frag_check') else None
    })


@bp.route('/api/fragmentacion/stop', methods=['GET'])
def stop_frag_scheduler():
    """Detiene el monitoreo de fragmentación."""
    global frag_is_running
    if not frag_is_running:
        return jsonify({'success': False, 'message': 'El monitoreo de fragmentación no está activo'})
    try:
        scheduler.remove_job('frag_check')
    except Exception:
        pass
    frag_is_running = False
    return jsonify({'success': True, 'message': 'Monitoreo de fragmentación detenido'})


@bp.route('/api/fragmentacion/status', methods=['GET'])
def frag_status():
    """Devuelve el estado actual del monitoreo de fragmentación."""
    job = scheduler.get_job('frag_check')
    next_run = str(job.next_run_time) if job else None
    return jsonify({
        'is_running': frag_is_running,
        'umbral': frag_umbral,
        'last_check': frag_last_check,
        'last_result': frag_last_result,
        'interval_minutes': FRAG_INTERVAL_MINUTES,
        'next_run': next_run
    })


@bp.route('/api/fragmentacion/test', methods=['GET'])
def test_fragmentation():
    """
    Endpoint de prueba: ejecuta la verificación de fragmentación manualmente.

    Query params:
        umbral (int): Porcentaje mínimo de fragmentación (default: valor configurado).
    """
    try:
        umbral = int(request.args.get('umbral', frag_umbral))
    except (ValueError, TypeError):
        umbral = frag_umbral

    print(f"[{datetime.now()}] TEST FRAGMENTACIÓN: verificando con umbral={umbral}%...")

    if _flask_app:
        with _flask_app.app_context():
            resultado = verificar_fragmentacion(umbral)
            log_auditoria(
                'VERIFICACIÓN',
                'Fragmentación',
                resultado['mensaje'],
                usuario='sistema',
                resultado='Alerta' if resultado['hay_alerta'] else 'Éxito'
            )
    else:
        resultado = verificar_fragmentacion(umbral)

    return jsonify({
        'success': True,
        'result': resultado
    })


# REPORTES INTERACTIVOS POR WHATSAPP
# ===========================================================================

def procesar_mensaje_reporte(texto_usuario, numero_usuario):
    """
    Procesa un mensaje del usuario para reportes interactivos.
    Gestiona el flujo de conversación y generación de reportes.
    """
    print(f"[DEBUG Reporte] Procesando mensaje de {numero_usuario}: '{texto_usuario}'")

    # Obtener la conversación
    conv = UserConversation.get_or_create(numero_usuario)
    texto_limpio = texto_usuario.strip().lower()
    print(f"[DEBUG Reporte] Estado actual de conversación: {conv.state}")

    # Si la conversación está inactiva y el usuario envía un número de reporte (1-5),
    # activamos el menú y procesamos la selección en el mismo paso.
    comandos_inicio = ['menu', 'reportes', 'iniciar', 'start']
    if conv.state == 'idle' and texto_limpio not in comandos_inicio:
        from services.interactive_reports_service import REPORT_TYPES
        if texto_limpio in REPORT_TYPES:
            print(f"[DEBUG Reporte] Usuario inactivo envió opción válida {texto_limpio}. "
                  "Activando menú y procesando selección.")
            conv.update_state('menu')
        else:
            print(f"[DEBUG Reporte] Conversación inactiva. Mensaje '{texto_limpio}' no es "
                  "comando válido. Se enviará menú.")
            # Enviar menú para que el usuario pueda iniciar la conversación
            from services.interactive_reports_service import generar_menu_principal
            send_message(generar_menu_principal(), numero_usuario)
            return {
                'processed': True,
                'user': numero_usuario,
                'estado': 'menu',
                'tipo_reporte': None,
                'reason': 'Conversación inactiva, menú enviado'
            }

    # Procesar el mensaje y obtener la respuesta del estado
    resultado_estado = procesar_mensaje_usuario(numero_usuario, texto_usuario)
    print(f"[DEBUG Reporte] Resultado de procesar_mensaje_usuario: {resultado_estado}")

    # Enviar respuesta inicial/menú
    if resultado_estado['respuesta']:
        send_result = send_message(resultado_estado['respuesta'], numero_usuario)
        if not send_result['success']:
            print(f"[ERROR] Fallo al enviar respuesta de reporte: {send_result}")

    # Si el usuario seleccionó un reporte, generarlo y enviarlo
    if resultado_estado['estado'] == 'generating_report' and resultado_estado['tipo_reporte']:
        tipo_reporte = resultado_estado['tipo_reporte']
        print(f"[DEBUG] Generando reporte: {tipo_reporte} para {numero_usuario}")

        resultado_reporte = generar_y_enviar_reporte(numero_usuario, tipo_reporte)
        print(f"[DEBUG] Resultado de generar_y_enviar_reporte: exito={resultado_reporte.get('exito')}, "
              f"pdf_path={resultado_reporte.get('pdf_path')}")

        if resultado_reporte['exito']:
            if resultado_reporte.get('pdf_path'):
                send_result = send_document(
                    resultado_reporte['pdf_path'],
                    numero_usuario,
                    resultado_reporte.get('mensaje', 'Reporte generado')
                )
                # Eliminar el PDF después de enviar
                try:
                    import os
                    if os.path.exists(resultado_reporte['pdf_path']):
                        os.remove(resultado_reporte['pdf_path'])
                        print(f"[OK] PDF eliminado: {resultado_reporte['pdf_path']}")
                except Exception as e:
                    print(f"[ERROR] No se pudo eliminar el PDF: {e}")
            else:
                send_result = send_message(resultado_reporte['mensaje'], numero_usuario)

            if send_result['success']:
                print(f"[OK] Reporte {tipo_reporte} enviado a {numero_usuario}")
                actualizar_estado_reporte_enviado(numero_usuario)
                from services.interactive_reports_service import generar_menu_continuar
                menu_continuar = generar_menu_continuar()
                send_message(menu_continuar, numero_usuario)
            else:
                print(f"[ERROR] Fallo al enviar reporte: {send_result}")
                send_message(f"❌ No se pudo enviar el reporte. Error: {send_result.get('error', send_result.get('status_code'))}", numero_usuario)
        else:
            print(f"[ERROR] Fallo en generación de reporte: {resultado_reporte}")
            send_message(resultado_reporte['mensaje'], numero_usuario)

    return {
        'processed': True,
        'user': numero_usuario,
        'estado': resultado_estado['estado'],
        'tipo_reporte': resultado_estado['tipo_reporte']
    }


# ===========================================================================
# ENDPOINTS PARA REPORTES AUTOMÁTICOS
# ===========================================================================

@bp.route('/api/reports/start', methods=['POST'])
def start_automatic_reports():
    """Inicia los reportes automáticos (programa daily/weekly/monthly y configura webhook)."""
    global reports_is_running, reports_destination, reports_daily_enabled, reports_weekly_enabled, reports_monthly_enabled
    global REPORTS_DAILY_HOUR, REPORTS_DAILY_MINUTE, REPORTS_WEEKLY_DAY, REPORTS_WEEKLY_HOUR, REPORTS_WEEKLY_MINUTE
    global REPORTS_MONTHLY_DAY, REPORTS_MONTHLY_HOUR, REPORTS_MONTHLY_MINUTE

    if reports_is_running:
        return jsonify({'success': False, 'message': 'Los reportes ya están activos'})

    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    if not phone_number:
        return jsonify({'success': False, 'message': 'Debes proporcionar un número de teléfono'}), 400
    is_valid, result = validate_phone(phone_number)
    if not is_valid:
        return jsonify({'success': False, 'message': result}), 400
    reports_destination = result

    # Actualizar configuraciones
    reports_daily_enabled = data.get('daily_enabled', True)
    reports_weekly_enabled = data.get('weekly_enabled', True)
    reports_monthly_enabled = data.get('monthly_enabled', True)

    REPORTS_DAILY_HOUR = data.get('daily_hour', REPORTS_DAILY_HOUR)
    REPORTS_DAILY_MINUTE = data.get('daily_minute', REPORTS_DAILY_MINUTE)
    REPORTS_WEEKLY_DAY = data.get('weekly_day', REPORTS_WEEKLY_DAY)
    REPORTS_WEEKLY_HOUR = data.get('weekly_hour', REPORTS_WEEKLY_HOUR)
    REPORTS_WEEKLY_MINUTE = data.get('weekly_minute', REPORTS_WEEKLY_MINUTE)
    REPORTS_MONTHLY_DAY = data.get('monthly_day', REPORTS_MONTHLY_DAY)
    REPORTS_MONTHLY_HOUR = data.get('monthly_hour', REPORTS_MONTHLY_HOUR)
    REPORTS_MONTHLY_MINUTE = data.get('monthly_minute', REPORTS_MONTHLY_MINUTE)

    print(f"[{datetime.now()}] Número de reportes actualizado: {reports_destination}")
    print(f"[INFO] Habilitados: Diario={reports_daily_enabled}, Semanal={reports_weekly_enabled}, Mensual={reports_monthly_enabled}")

    # Configurar webhook para recibir respuestas de WhatsApp
    try:
        webhook_ok = configure_evolution_webhook()
        if webhook_ok:
            print(f"[OK] Webhook de WhatsApp configurado para reportes interactivos")
        else:
            print(f"[WARN] No se pudo configurar el webhook de WhatsApp para reportes interactivos")
    except Exception as e:
        print(f"[WARN] Error configurando webhook de WhatsApp: {e}")

    reports_is_running = True

    # Programar los trabajos de reportes automáticos solo si están habilitados
    try:
        # Limpiar jobs anteriores
        for job_id in ['daily_reports', 'weekly_reports', 'monthly_reports']:
            try:
                scheduler.remove_job(job_id)
            except Exception:
                pass
        
        # Reportes diarios
        if reports_daily_enabled:
            scheduler.add_job(
                execute_daily_report,
                trigger=CronTrigger(
                    hour=REPORTS_DAILY_HOUR,
                    minute=REPORTS_DAILY_MINUTE,
                    timezone=REPORTS_TIMEZONE
                ),
                id='daily_reports',
                replace_existing=True
            )
            print(f"[OK] Reporte diario programado para {REPORTS_DAILY_HOUR:02d}:{REPORTS_DAILY_MINUTE:02d}")
        
        # Reportes semanales
        if reports_weekly_enabled:
            scheduler.add_job(
                execute_weekly_report,
                trigger=CronTrigger(
                    day_of_week=REPORTS_WEEKLY_DAY,
                    hour=REPORTS_WEEKLY_HOUR,
                    minute=REPORTS_WEEKLY_MINUTE,
                    timezone=REPORTS_TIMEZONE
                ),
                id='weekly_reports',
                replace_existing=True
            )
            print(f"[OK] Reporte semanal programado para {REPORTS_WEEKLY_DAY} {REPORTS_WEEKLY_HOUR:02d}:{REPORTS_WEEKLY_MINUTE:02d}")
        
        # Reportes mensuales
        if reports_monthly_enabled:
            scheduler.add_job(
                execute_monthly_report,
                trigger=CronTrigger(
                    day=REPORTS_MONTHLY_DAY,
                    hour=REPORTS_MONTHLY_HOUR,
                    minute=REPORTS_MONTHLY_MINUTE,
                    timezone=REPORTS_TIMEZONE
                ),
                id='monthly_reports',
                replace_existing=True
            )
            print(f"[OK] Reporte mensual programado para día {REPORTS_MONTHLY_DAY} {REPORTS_MONTHLY_HOUR:02d}:{REPORTS_MONTHLY_MINUTE:02d}")
        
        print(f"[OK] Reportes automáticos configurados para {reports_destination}")
    except Exception as e:
        print(f"[ERROR] Error al programar reportes automáticos: {e}")

    return jsonify({
        'success': True,
        'message': f'Reportes automáticos programados para el número {reports_destination}',
        'destination': reports_destination,
        'daily_enabled': reports_daily_enabled,
        'weekly_enabled': reports_weekly_enabled,
        'monthly_enabled': reports_monthly_enabled,
    })


@bp.route('/api/reports/stop', methods=['GET'])
def stop_automatic_reports():
    """Detiene los reportes automáticos."""
    global reports_is_running
    
    if not reports_is_running:
        return jsonify({'success': False, 'message': 'Los reportes automáticos no están activos'})
    
    try:
        scheduler.remove_job('daily_reports')
        scheduler.remove_job('weekly_reports')
        scheduler.remove_job('monthly_reports')
    except Exception as e:
        print(f"[WARN] Error al remover trabajos: {e}")
    
    reports_is_running = False
    return jsonify({'success': True, 'message': 'Reportes automáticos detenidos'})


@bp.route('/api/reports/toggle', methods=['POST'])
def toggle_report_enabled():
    """Toggles the enabled state of a specific report type (daily/weekly/monthly)."""
    global reports_daily_enabled, reports_weekly_enabled, reports_monthly_enabled

    data = request.get_json() or {}
    report_type = data.get('type')  # 'daily', 'weekly', or 'monthly'
    enabled = data.get('enabled')

    if report_type not in ['daily', 'weekly', 'monthly']:
        return jsonify({'success': False, 'message': 'Invalid report type'}), 400

    if enabled is None:
        return jsonify({'success': False, 'message': 'Enabled state is required'}), 400

    # Update the global state
    if report_type == 'daily':
        reports_daily_enabled = enabled
        if reports_is_running:
            if enabled:
                scheduler.add_job(
                    execute_daily_report,
                    trigger=CronTrigger(
                        hour=REPORTS_DAILY_HOUR,
                        minute=REPORTS_DAILY_MINUTE,
                        timezone=REPORTS_TIMEZONE
                    ),
                    id='daily_reports',
                    replace_existing=True
                )
            else:
                try:
                    scheduler.remove_job('daily_reports')
                except Exception:
                    pass
    elif report_type == 'weekly':
        reports_weekly_enabled = enabled
        if reports_is_running:
            if enabled:
                scheduler.add_job(
                    execute_weekly_report,
                    trigger=CronTrigger(
                        day_of_week=REPORTS_WEEKLY_DAY,
                        hour=REPORTS_WEEKLY_HOUR,
                        minute=REPORTS_WEEKLY_MINUTE,
                        timezone=REPORTS_TIMEZONE
                    ),
                    id='weekly_reports',
                    replace_existing=True
                )
            else:
                try:
                    scheduler.remove_job('weekly_reports')
                except Exception:
                    pass
    elif report_type == 'monthly':
        reports_monthly_enabled = enabled
        if reports_is_running:
            if enabled:
                scheduler.add_job(
                    execute_monthly_report,
                    trigger=CronTrigger(
                        day=REPORTS_MONTHLY_DAY,
                        hour=REPORTS_MONTHLY_HOUR,
                        minute=REPORTS_MONTHLY_MINUTE,
                        timezone=REPORTS_TIMEZONE
                    ),
                    id='monthly_reports',
                    replace_existing=True
                )
            else:
                try:
                    scheduler.remove_job('monthly_reports')
                except Exception:
                    pass

    return jsonify({
        'success': True,
        'message': f'Reporte {report_type} {"habilitado" if enabled else "deshabilitado"}',
        'daily_enabled': reports_daily_enabled,
        'weekly_enabled': reports_weekly_enabled,
        'monthly_enabled': reports_monthly_enabled
    })


@bp.route('/api/reports/status', methods=['GET'])
def get_reports_status():
    """Obtiene el estado de los reportes automáticos."""
    daily_job = scheduler.get_job('daily_reports')
    weekly_job = scheduler.get_job('weekly_reports')
    monthly_job = scheduler.get_job('monthly_reports')
    
    return jsonify({
        'is_running': reports_is_running,
        'destination': reports_destination,
        'last_daily': reports_last_daily,
        'last_weekly': reports_last_weekly,
        'last_monthly': reports_last_monthly,
        'daily_enabled': reports_daily_enabled,
        'weekly_enabled': reports_weekly_enabled,
        'monthly_enabled': reports_monthly_enabled,
        'daily': {
            'time': f'{REPORTS_DAILY_HOUR:02d}:{REPORTS_DAILY_MINUTE:02d}',
            'types': REPORTS_DAILY_TYPES,
            'next_run': str(daily_job.next_run_time) if daily_job else None
        },
        'weekly': {
            'day': REPORTS_WEEKLY_DAY,
            'time': f'{REPORTS_WEEKLY_HOUR:02d}:{REPORTS_WEEKLY_MINUTE:02d}',
            'types': REPORTS_WEEKLY_TYPES,
            'next_run': str(weekly_job.next_run_time) if weekly_job else None
        },
        'monthly': {
            'day': REPORTS_MONTHLY_DAY,
            'time': f'{REPORTS_MONTHLY_HOUR:02d}:{REPORTS_MONTHLY_MINUTE:02d}',
            'types': REPORTS_MONTHLY_TYPES,
            'next_run': str(monthly_job.next_run_time) if monthly_job else None
        },
        'timezone': REPORTS_TIMEZONE
    })


@bp.route('/api/reports/test-daily', methods=['GET'])
def test_daily_reports():
    """Ejecuta manualmente un reporte automático diario para pruebas."""
    print(f"[{datetime.now()}] TEST-DAILY: Ejecutando reporte automático diario manual...")
    
    if _flask_app:
        with _flask_app.app_context():
            execute_daily_report()
    else:
        execute_daily_report()
    
    return jsonify({
        'success': True,
        'message': 'Reporte automático diario ejecutado manualmente. Revisa tu WhatsApp.',
        'destination': reports_destination,
        'last_daily': reports_last_daily,
        'types': REPORTS_DAILY_TYPES
    })


@bp.route('/api/reports/test-weekly', methods=['GET'])
def test_weekly_reports():
    """Ejecuta manualmente un reporte automático semanal para pruebas."""
    print(f"[{datetime.now()}] TEST-WEEKLY: Ejecutando reporte automático semanal manual...")
    
    if _flask_app:
        with _flask_app.app_context():
            execute_weekly_report()
    else:
        execute_weekly_report()
    
    return jsonify({
        'success': True,
        'message': 'Reporte automático semanal ejecutado manualmente. Revisa tu WhatsApp.',
        'destination': reports_destination,
        'last_weekly': reports_last_weekly,
        'types': REPORTS_WEEKLY_TYPES
    })


@bp.route('/api/reports/test-monthly', methods=['GET'])
def test_monthly_reports():
    """Ejecuta manualmente un reporte automático mensual para pruebas."""
    print(f"[{datetime.now()}] TEST-MONTHLY: Ejecutando reporte automático mensual manual...")
    
    if _flask_app:
        with _flask_app.app_context():
            execute_monthly_report()
    else:
        execute_monthly_report()
    
    return jsonify({
        'success': True,
        'message': 'Reporte automático mensual ejecutado manualmente. Revisa tu WhatsApp.',
        'destination': reports_destination,
        'last_monthly': reports_last_monthly,
        'types': REPORTS_MONTHLY_TYPES
    })


@bp.route('/api/reports/interactive', methods=['GET'])
def get_interactive_status():
    """Obtiene el estado de las conversaciones interactivas."""
    return jsonify({
        'available_reports': {
            key: {
                'nombre': report['nombre'],
                'descripcion': report['descripcion']
            }
            for key, report in REPORT_TYPES.items()
        },
        'message': 'Envía un mensaje por WhatsApp a la conversación activa para iniciar un reporte interactivo'

# ===========================================================================
# TEST DE WHATSAPP (PARTE INICIAL DE CONFLICTO DE ANTHONY)
# ===========================================================================

@bp.route('/api/test-whatsapp', methods=['POST'])
def test_whatsapp():
    """Prueba el envío de mensajes por WhatsApp."""
    data = request.get_json() or {}
    destination = data.get('destination', login_security_destination if login_security_destination else current_destination)
    message = data.get('message', "✅ ¡Prueba exitosa de Evolution API!")
    result = send_message(message, destination)
    return jsonify(result)

# ===========================================================================
# MONITOREO DE SEGURIDAD DE LOGIN
# ===========================================================================

def _check_login_security_impl():
    """Implementación interna de la verificación de seguridad de login."""
    global login_security_last_check, login_security_last_alert

    print("\n[DEBUG SEGURO] [SCHEDULER] Ejecutando verificación periódica de seguridad de login...")
    print(f"[DEBUG SEGURO] [SCHEDULER] Número destino configurado: {login_security_destination}")
    login_security_last_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Ejecutar verificación y capturar info de alerta
    alert_info = check_failed_attempts(login_security_destination)

    # Si se envió una alerta, actualizar la variable global
    if alert_info:
        login_security_last_alert = alert_info
        print(f"[DEBUG SEGURO] [ALERTA] Última alerta registrada: {alert_info}")


def check_login_security():
    """Función ejecutada por APScheduler dentro de Flask app_context."""
    if _flask_app:
        with _flask_app.app_context():
            _check_login_security_impl()
    else:
        print("[ERROR] No se ha configurado la app Flask.")


@bp.route('/api/login-security/start', methods=['POST'])
def start_login_security():
    """Inicia el monitoreo de seguridad de login."""
    global login_security_is_running, login_security_destination

    print("\n[DEBUG SEGURO] [START] Endpoint /api/login-security/start llamado!")
    print(f"[DEBUG SEGURO] [START] login_security_is_running actualmente: {login_security_is_running}")

    if login_security_is_running:
        print(f"[DEBUG SEGURO] [START] El monitoreo ya está activo, devolviendo error...")
        return jsonify({'success': False, 'message': 'El monitoreo de seguridad de login ya está activo'})

    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    print(f"[DEBUG SEGURO] [START] Número recibido del frontend: '{phone_number}'")
    
    if phone_number:
        is_valid, result = validate_phone(phone_number)
        print(f"[DEBUG SEGURO] [START] Resultado de validate_phone: is_valid={is_valid}, result={result}")
        
        if not is_valid:
            return jsonify({'success': False, 'message': result}), 400
        login_security_destination = result
        print(f"[DEBUG SEGURO] [START] login_security_destination actualizado a: {login_security_destination}")

    print(f"[DEBUG SEGURO] [START] Agregando job al scheduler con intervalo de {LOGIN_CHECK_INTERVAL_MINUTES} minutos...")
    scheduler.add_job(
        check_login_security,
        'interval',
        minutes=LOGIN_CHECK_INTERVAL_MINUTES,
        id='login_security_check',
        replace_existing=True
    )
    print(f"[DEBUG SEGURO] [START] Job agregado al scheduler correctamente!")

    login_security_is_running = True
    
    print(f"[DEBUG SEGURO] [START] Ejecutando verificación INMEDIATA (no esperar el primer intervalo)!")
    check_login_security()
    
    job = scheduler.get_job('login_security_check')
    next_run = str(job.next_run_time) if job else None
    print(f"[DEBUG SEGURO] [START] Próxima ejecución programada para: {next_run}")

    return jsonify({
        'success': True,
        'message': f'Monitoreo de seguridad de login iniciado. Verificación cada {LOGIN_CHECK_INTERVAL_MINUTES} minutos.',
        'destination': login_security_destination,
        'interval_minutes': LOGIN_CHECK_INTERVAL_MINUTES,
        'next_run': next_run
    })


@bp.route('/api/login-security/stop', methods=['GET'])
def stop_login_security():
    """Detiene el monitoreo de seguridad de login."""
    global login_security_is_running
    if not login_security_is_running:
        return jsonify({'success': False, 'message': 'El monitoreo de seguridad de login no está activo'})
    try:
        scheduler.remove_job('login_security_check')
    except Exception:
        pass
    login_security_is_running = False
    return jsonify({'success': True, 'message': 'Monitoreo de seguridad de login detenido'})


@bp.route('/api/login-security/status', methods=['GET'])
def login_security_status():
    """Devuelve el estado actual del monitoreo de seguridad de login."""
    import services.login_security_service as ls_service
    job = scheduler.get_job('login_security_check')
    next_run = str(job.next_run_time) if job else None
    return jsonify({
        'is_running': login_security_is_running,
        'destination': login_security_destination,
        'last_check': login_security_last_check,
        'last_alert': login_security_last_alert,  # Nueva información
        'next_run': next_run,
        'interval_minutes': LOGIN_CHECK_INTERVAL_MINUTES,
        'failed_attempts': ls_service.failed_attempts,
        'pending_alerts': ls_service.pending_alerts
    })


@bp.route('/api/login-security/test', methods=['GET'])
def test_login_security():
    """Endpoint de prueba: ejecuta la verificación de seguridad de login manualmente."""
    import services.login_security_service as ls_service
    global login_security_last_check, login_security_last_alert

    print(f"\n[DEBUG SEGURO] [TEST] Endpoint /api/login-security/test llamado!")
    print(f"[DEBUG SEGURO] [TEST] Ejecutando verificación manual...")
    login_security_last_check = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Ejecutar verificación y capturar info de alerta
    alert_info = check_failed_attempts(login_security_destination)

    # Si se envió una alerta, actualizar la variable global
    if alert_info:
        login_security_last_alert = alert_info
        print(f"[DEBUG SEGURO] [ALERTA] Última alerta registrada: {alert_info}")

    print(f"[DEBUG SEGURO] [TEST] Verificación manual completada!")
    return jsonify({
        'success': True,
        'message': 'Verificación de seguridad de login ejecutada manualmente. Revisa la consola de Flask y tu WhatsApp.',
        'destination': login_security_destination,
        'debug_info': {
            'failed_attempts': ls_service.failed_attempts,
            'pending_alerts': ls_service.pending_alerts,
            'current_pending_alert_username': ls_service.current_pending_alert_username,
            'last_alert': login_security_last_alert
        }
    })


@bp.route('/api/login-security/debug', methods=['GET'])
def debug_login_security():
    """Endpoint de depuración: muestra el estado actual del sistema de seguridad login."""
    import services.login_security_service as ls_service
    return jsonify({
        'success': True,
        'destination': login_security_destination,
        'debug_info': {
            'failed_attempts': ls_service.failed_attempts,
            'pending_alerts': ls_service.pending_alerts,
            'last_processed_log_id': ls_service.last_processed_log_id,
            'last_processed_error_time': ls_service.last_processed_error_time,
            'current_pending_alert_username': ls_service.current_pending_alert_username
        }
    })


@bp.route('/api/login-security/reset', methods=['POST'])
def reset_login_security():
    """Resetea TODO el estado del monitoreo de seguridad de login (para pruebas)."""
    import services.login_security_service as ls_service
    global login_security_last_check, login_security_last_alert

    ls_service.failed_attempts = {}
    ls_service.pending_alerts = {}
    ls_service.last_processed_log_id = 0
    ls_service.last_processed_error_time = None
    ls_service.current_pending_alert_username = None
    login_security_last_check = None
    login_security_last_alert = None

    return jsonify({
        'success': True,
        'message': 'Estado del monitoreo de seguridad de login reseteado COMPLETAMENTE!'
    })


@bp.route('/api/login-security/simulate-failure', methods=['POST'])
def simulate_login_failure():
    """
    Endpoint de prueba: simula un intento fallido de login para pruebas
    insertando un registro directamente en la tabla AuditoriaLoginsFallidos.
    """
    data = request.get_json() or {}
    username = data.get('username', 'test_user')

    from services.login_security_service import simulate_failed_login

    resultado = simulate_failed_login(username)

    return jsonify({
        'success': resultado['exito'],
        'message': resultado['mensaje'],
        'username': username
    })
