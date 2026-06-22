"""
Backend Flask - Dashboard Tenebrosa
====================================

API REST para controlar el envío periódico de mensajes de WhatsApp
con información de la base de datos TenebrosaOLTP.

Endpoints:
  GET  /api/health     → Verificar estado
  GET  /api/start      → Iniciar disparo (envía inmediatamente + cada 2 min)
  GET  /api/stop       → Detener disparo
  GET  /api/status     → Estado actual
  GET  /api/tables     → Obtener información de tablas (sin enviar)
"""

import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from database import get_tables_info
from whatsapp import send_message, format_tables_message

load_dotenv()

app = Flask(__name__)
CORS(app)

# Estado global
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
    
    # Quitar espacios y signo +
    cleaned = number.replace(' ', '').replace('+', '')
    
    # Debe ser solo dígitos
    if not cleaned.isdigit():
        return False, "El número solo debe contener dígitos"
    
    # Debe tener entre 10 y 13 dígitos
    if len(cleaned) < 10:
        return False, f"El número es muy corto ({len(cleaned)} dígitos). Mínimo 10."
    if len(cleaned) > 13:
        return False, f"El número es muy largo ({len(cleaned)} dígitos). Máximo 13."
    
    return True, cleaned


def execute_send():
    """
    Función que se ejecuta periódicamente:
    1. Consulta tablas de SQL Server
    2. Formatea mensaje
    3. Envía por WhatsApp al número actual
    """
    global last_sent, last_message
    
    print(f"[{datetime.now()}] Ejecutando envío programado a {current_destination}...")
    
    # Obtener info de tablas
    tables_info = get_tables_info()
    
    if 'error' in tables_info:
        print(f"[ERROR] No se pudo obtener tablas: {tables_info['error']}")
        last_message = f"Error: {tables_info['error']}"
        return
    
    # Formatear mensaje
    message = format_tables_message(tables_info)
    
    # Enviar WhatsApp al número actual
    result = send_message(message, current_destination)
    
    if result['success']:
        last_sent = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last_message = message[:100] + "..." if len(message) > 100 else message
        print(f"[OK] Mensaje enviado a {current_destination} a las {last_sent}")
    else:
        error_msg = result.get('error', f"Status {result.get('status_code', 'unknown')}")
        last_message = f"Error al enviar: {error_msg}"
        print(f"[ERROR] {last_message}")


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'is_running': is_running,
        'last_sent': last_sent,
        'last_message': last_message,
        'destination': current_destination,
        'interval_minutes': INTERVAL_MINUTES
    })


@app.route('/api/test-send', methods=['GET'])
def test_send():
    """Endpoint de prueba para enviar un mensaje inmediato."""
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


@app.route('/api/start', methods=['POST'])
def start_scheduler():
    global is_running, current_destination
    
    if is_running:
        return jsonify({
            'success': False,
            'message': 'El disparo ya está activo'
        })
    
    # Obtener número del body
    data = request.get_json() or {}
    phone_number = data.get('number', '').strip()
    
    # Validar número
    if phone_number:
        is_valid, result = validate_phone(phone_number)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': result
            }), 400
        current_destination = result
        print(f"[{datetime.now()}] Número actualizado: {current_destination}")
    
    # Ejecutar inmediatamente la primera vez
    execute_send()
    
    # Programar cada 1 minuto
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


@app.route('/api/stop', methods=['GET'])
def stop_scheduler():
    global is_running
    
    if not is_running:
        return jsonify({
            'success': False,
            'message': 'El disparo no está activo'
        })
    
    scheduler.remove_job('whatsapp_disparo')
    is_running = False
    
    return jsonify({
        'success': True,
        'message': 'Disparo detenido'
    })


@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Obtiene información de tablas sin enviar mensaje."""
    tables_info = get_tables_info()
    return jsonify(tables_info)


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"="*60)
    print(f"  TENEBROSA DASHBOARD - BACKEND")
    print(f"="*60)
    print(f"  API: http://localhost:{port}")
    print(f"  Evolution API: {os.getenv('EVOLUTION_URL')}")
    print(f"  Destino WhatsApp: {current_destination}")
    print(f"="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
