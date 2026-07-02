"""
Módulo de envío de WhatsApp via Evolution API
============================================

Envía mensajes a través de Evolution API.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_URL = os.getenv('EVOLUTION_URL', 'http://localhost:8080')
API_KEY = os.getenv('EVOLUTION_API_KEY', 'mi-api-key-secreta-123')
INSTANCE = os.getenv('EVOLUTION_INSTANCE', 'mi-whatsapp')
DESTINATION = os.getenv('WHATSAPP_DESTINATION', '51952310138')

HEADERS = {
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}


def send_message(text, number=None):
    """
    Envía un mensaje de WhatsApp.
    
    Args:
        text: Texto del mensaje a enviar
        number: Número de destino (opcional, usa DESTINATION por defecto)
        
    Returns:
        dict: Resultado del envío
    """
    target_number = number or DESTINATION
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
    payload = {
        'number': target_number,
        'text': text
    }
    
    try:
        print(f"[DEBUG WhatsApp] POST {url}")
        # Print safely without encoding errors
        print(f"[DEBUG WhatsApp] Headers: apikey=***, Content-Type={HEADERS['Content-Type']}")
        # Use repr to safely print payload
        print(f"[DEBUG WhatsApp] Payload: {repr(payload)}")
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        print(f"[DEBUG WhatsApp] Status: {response.status_code}")
        print(f"[DEBUG WhatsApp] Response: {repr(response.text[:500])}")
        try:
            data = response.json()
        except Exception:
            data = {'raw': response.text}

        return {
            'success': response.status_code == 201,
            'status_code': response.status_code,
            'response': data
        }

    except Exception as e:
        print(f"[DEBUG WhatsApp] Exception: {repr(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def format_tables_message(tables_info):
    """
    Formatea el mensaje con información de tablas.
    
    Args:
        tables_info: dict con 'count' y 'names'
        
    Returns:
        str: Mensaje formateado
    """
    count = tables_info.get('count', 0)
    names = tables_info.get('names', [])
    
    if count == 0:
        return "No se encontraron tablas en la base de datos Bibliouni."
    
    # Limitar lista si es muy larga
    if len(names) > 20:
        names_text = ', '.join(names[:20]) + f" y {len(names) - 20} tablas más..."
    else:
        names_text = ', '.join(names)
    
    message = (
        f"📊 *Reporte de Base de Datos*\n\n"
        f"Base de datos: *Bibliouni*\n"
        f"Total de tablas: *{count}*\n\n"
        f"*Tablas:*\n{names_text}"
    )
    
    return message


if __name__ == '__main__':
    # Prueba
    result = send_message("Mensaje de prueba desde el dashboard")
    print(result)
