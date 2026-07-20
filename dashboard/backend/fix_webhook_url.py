"""
Reconfigura el webhook de Evolution API a la IP correcta del host Windows.
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_URL = os.getenv('EVOLUTION_URL', 'http://localhost:8081')
API_KEY = os.getenv('EVOLUTION_API_KEY', 'mi-api-key-secreta-123')
INSTANCE = os.getenv('EVOLUTION_INSTANCE', 'jean')

# IP del host Windows que Docker puede alcanzar (confirmada arriba)
HOST_IP = '192.168.56.1'
NUEVA_URL = f'http://{HOST_IP}:5000/api/backup/webhook'

print(f'Reconfigurando webhook de Evolution API...')
print(f'Nueva URL: {NUEVA_URL}')

headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}

# Reconfigurar webhook
set_url = f'{EVOLUTION_URL}/webhook/set/{INSTANCE}'
payload = {
    'webhook': {
        'enabled': True,
        'url': NUEVA_URL,
        'webhook_by_events': False,
        'webhook_base64': False,
        'events': ['MESSAGES_UPSERT']
    }
}

r = requests.post(set_url, headers=headers, json=payload, timeout=10)
print(f'HTTP Status: {r.status_code}')
print(f'Respuesta: {json.dumps(r.json(), indent=2)}')

# Verificar configuración guardada
find_url = f'{EVOLUTION_URL}/webhook/find/{INSTANCE}'
r2 = requests.get(find_url, headers=headers, timeout=10)
config = r2.json()
print(f'\nWebhook URL guardada: {config.get("url")}')
print(f'Enabled: {config.get("enabled")}')
print(f'Events: {config.get("events")}')

if config.get('url') == NUEVA_URL:
    print('\nOK - Webhook reconfigurado correctamente!')
    print('Ahora cuando envíes RESUELVE BACKUP desde WhatsApp,')
    print(f'Evolution API enviará el mensaje a: {NUEVA_URL}')
else:
    print(f'\nADVERTENCIA: La URL guardada no coincide con la esperada.')
    print(f'Esperado: {NUEVA_URL}')
    print(f'Guardado: {config.get("url")}')
