"""
Blueprint del módulo Disparador.
Se conecta a Bibliouni vía db_tenebrosa.py y whatsapp.py.
"""

import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from db_tenebrosa import get_tables_info
from whatsapp import send_message, format_tables_message

bp = Blueprint('disparador', __name__)

# Estado global del disparador
is_running = False
last_sent = None
last_message = None
current_destination = os.getenv('WHATSAPP_DESTINATION', '51952310138')
scheduler = BackgroundScheduler()
scheduler.start()

INTERVAL_MINUTES = 1


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
