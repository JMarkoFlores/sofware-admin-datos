"""
Blueprint del módulo Disparador.
Se conecta a Bibliouni vía db_tenebrosa.py y whatsapp.py.

Extensiones incluidas:
- Disparador de mensajes (INTACTO)
- Monitoreo de backup diario a las 7:00 AM (America/Lima)
- Webhook para recepción de comandos vía Evolution API
"""

import os
import requests
from datetime import datetime
from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from db_tenebrosa import get_tables_info
from whatsapp import send_message, format_tables_message
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
        return jsonify({'success': False, 'message': 'El disparo ya está activo'})
    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    if phone_number:
        is_valid, result = validate_phone(phone_number)
        if not is_valid:
            return jsonify({'success': False, 'message': result}), 400
        current_destination = result
        print(f"[{datetime.now()}] Número actualizado: {current_destination}")
    execute_send()
    scheduler.add_job(
        execute_send,
        'interval',
        minutes=INTERVAL_MINUTES,
        id='whatsapp_disparo',
        replace_existing=True
    )
    is_running = True
    return jsonify({
        'success': True,
        'message': f'Disparo iniciado. Enviando cada {INTERVAL_MINUTES} minuto.',
        'destination': current_destination
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
    """Inicia el monitoreo de backup (configura webhook + programa cron 7:00 AM)."""
    global backup_is_running, backup_destination

    if backup_is_running:
        return jsonify({'success': False, 'message': 'El monitoreo de backup ya está activo'})

    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    if phone_number:
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
        'message': f'Monitoreo de backup iniciado. Verificación diaria a las {BACKUP_CHECK_HOUR:02d}:{BACKUP_CHECK_MINUTE:02d} ({BACKUP_TIMEZONE}).',
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

    # Extraer datos del payload de Evolution API v2
    data = payload.get('data', {})
    key = data.get('key', {})
    message = data.get('message', {})

    remote_jid = key.get('remoteJid', '')
    from_me = key.get('fromMe', True)
    text = message.get('conversation', '')

    # Limpiar número (quitar @s.whatsapp.net)
    numero_remoto = remote_jid.split('@')[0] if remote_jid else ''

    # Ignorar mensajes propios o sin texto
    if from_me or not text or not numero_remoto:
        return jsonify({'processed': False, 'reason': 'Ignored'}), 200

    print(f"[{datetime.now()}] Webhook recibido de {numero_remoto}: {text}")

    texto_upper = text.strip().upper()

    # Ejecutar procesamiento dentro de app_context para que
    # log_auditoria y db.session funcionen correctamente
    if texto_upper.startswith('FACTOR LLENADO'):
        # Comando de fill factor: FACTOR LLENADO <porcentaje>
        if _flask_app:
            with _flask_app.app_context():
                resultado = procesar_comando_fill_factor(text, numero_remoto, backup_destination)
        else:
            print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
            resultado = procesar_comando_fill_factor(text, numero_remoto, backup_destination)
    elif texto_upper.startswith('BLOQUEA'):
        # Comando de seguridad de login: BLOQUEA <username>
        if _flask_app:
            with _flask_app.app_context():
                resultado = procesar_comando_login(text, numero_remoto, login_security_destination)
        else:
            print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
            resultado = procesar_comando_login(text, numero_remoto, login_security_destination)
    else:
        # Comando de backup: RESUELVE BACKUP (u otros futuros)
        if _flask_app:
            with _flask_app.app_context():
                resultado = procesar_comando_backup(text, numero_remoto, backup_destination)
        else:
            print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
            resultado = procesar_comando_backup(text, numero_remoto, backup_destination)

    return jsonify(resultado), 200


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


# ===========================================================================
# TEST DE WHATSAPP
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
