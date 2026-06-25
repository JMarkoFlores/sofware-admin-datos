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
    Procesa el comando RESUELVE BACKUP.
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

    # Ejecutar procesamiento dentro de app_context para que
    # log_auditoria y db.session funcionen correctamente
    if _flask_app:
        with _flask_app.app_context():
            resultado = procesar_comando_backup(text, numero_remoto, backup_destination)
    else:
        print("[WARN] _flask_app no está configurado. Ejecutando sin app_context.")
        resultado = procesar_comando_backup(text, numero_remoto, backup_destination)

    return jsonify(resultado), 200
