"""
Módulo de envío de WhatsApp via Evolution API
============================================

Envía mensajes a través de Evolution API.
"""

import os
import requests
from dotenv import load_dotenv
from utils.helpers import log_auditoria

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
    NO envía a grupos (JIDs que terminan con @g.us).
    
    Args:
        text: Texto del mensaje a enviar
        number: Número de destino (opcional, usa DESTINATION por defecto)
        
    Returns:
        dict: Resultado del envío
    """
    target_number = number or DESTINATION
    
    # Evitar enviar a grupos
    if '@g.us' in str(target_number):
        print(f"[ERROR] Intento de enviar mensaje a grupo, cancelado: {target_number}")
        return {'success': False, 'error': 'No se puede enviar a grupos'}
        
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
    payload = {
        'number': target_number,
        'text': text
    }
    
    try:
        print(f"[DEBUG WhatsApp] Enviando mensaje a {target_number}")
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

        success = response.status_code in (200, 201)
        
        if success:
            print(f"[OK WhatsApp] Mensaje enviado correctamente a {target_number}")
        else:
            print(f"[ERROR WhatsApp] Fallo al enviar mensaje: {response.status_code}")
            
        log_auditoria(
            'WHATSAPP',
            'WhatsApp',
            f'Envío de mensaje por WhatsApp a {target_number}',
            usuario='sistema',
            resultado='Éxito' if success else 'Fallo',
            detalle=f'Status: {response.status_code}; Texto: {text[:160]}'
        )

        return {
            'success': success,
            'status_code': response.status_code,
            'response': data
        }

    except Exception as e:
        print(f"[ERROR WhatsApp] Excepción al enviar mensaje: {e}")
        log_auditoria(
            'WHATSAPP',
            'WhatsApp',
            f'Error al enviar mensaje por WhatsApp a {target_number}',
            usuario='sistema',
            resultado='Fallo',
            detalle=str(e)
        )
        return {
            'success': False,
            'error': str(e)
        }


def send_document(file_path, number=None, caption=None):
    """Envía un documento PDF por WhatsApp usando Evolution API."""
    import base64
    target_number = number or DESTINATION
    
    # Evitar enviar a grupos
    if '@g.us' in str(target_number):
        print(f"[ERROR] Intento de enviar documento a grupo, cancelado: {target_number}")
        return {'success': False, 'error': 'No se puede enviar a grupos'}
        
    if not file_path or not os.path.exists(file_path):
        return {'success': False, 'error': 'Archivo no encontrado'}

    url = f"{EVOLUTION_URL}/message/sendMedia/{INSTANCE}"
    
    try:
        # Leer archivo y convertir a base64 PURO (sin data URI prefix)
        with open(file_path, 'rb') as f:
            file_data = f.read()
        base64_data = base64.b64encode(file_data).decode('utf-8')
        filename = os.path.basename(file_path)
        
        # Construir payload correctamente para Evolution API (top-level, no nesting)
        payload = {
            "number": target_number,
            "mediatype": "document",
            "mimetype": "application/pdf",
            "caption": caption or "Reporte generado",
            "media": base64_data,
            "fileName": filename
        }
        
        headers = {
            "apikey": API_KEY,
            "Content-Type": "application/json"
        }
        
        print(f"[DEBUG WhatsApp] Enviando documento a {target_number}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"[DEBUG WhatsApp] Status: {response.status_code}, Response: {response.text[:500]}")
        
        success = response.status_code in (200, 201)
        
        if success:
            print(f"[OK WhatsApp] Documento enviado correctamente a {target_number}")
            log_auditoria(
                'WHATSAPP',
                'WhatsApp',
                f'Envío de PDF por WhatsApp a {target_number}',
                usuario='sistema',
                resultado='Éxito',
                detalle=f'Status: {response.status_code}; Archivo: {file_path}'
            )
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.text[:500]
            }
        else:
            print(f"[ERROR WhatsApp] Fallo al enviar documento: {response.status_code}")
            log_auditoria(
                'WHATSAPP',
                'WhatsApp',
                f'Fallo envío de PDF por WhatsApp a {target_number}',
                usuario='sistema',
                resultado='Fallo',
                detalle=f'Status: {response.status_code}; Archivo: {file_path}; Response: {response.text[:500]}'
            )
            return {
                'success': False,
                'status_code': response.status_code,
                'response': response.text[:500]
            }

    except Exception as e:
        print(f"[ERROR WhatsApp] Excepción al enviar documento: {e}")
        log_auditoria(
            'WHATSAPP',
            'WhatsApp',
            f'Error al enviar PDF por WhatsApp a {target_number}',
            usuario='sistema',
            resultado='Fallo',
            detalle=str(e)
        )
        return {'success': False, 'error': str(e)}


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
