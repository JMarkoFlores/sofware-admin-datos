import requests
import json

BASE_URL = 'http://localhost:5000'

print('=== PRUEBA COMPLETA DEL SISTEMA ===')

# 1. Verificar health
print('\n1. Health check...')
r = requests.get(f'{BASE_URL}/api/health')
print(f'   Status: {r.status_code}')

# 2. Verificar estado
print('\n2. Estado actual...')
r = requests.get(f'{BASE_URL}/api/status')
data = r.json()
print(f'   Status: {r.status_code}')
print(f'   is_running: {data.get("is_running")}')
print(f'   last_message: {data.get("last_message")}')

# 3. Obtener tablas
print('\n3. Obteniendo tablas de SQL Server...')
r = requests.get(f'{BASE_URL}/api/tables')
data = r.json()
print(f'   Status: {r.status_code}')
print(f'   Tablas encontradas: {data.get("count")}')
if data.get('names'):
    print(f'   Primeras tablas: {data["names"][:5]}')
if data.get('error'):
    print(f'   ERROR: {data["error"]}')

# 4. Prueba de envío directo
print('\n4. Prueba de envío directo a WhatsApp...')
r = requests.get(f'{BASE_URL}/api/test-send')
data = r.json()
print(f'   Status: {r.status_code}')
print(f'   Success: {data.get("success")}')
print(f'   Result: {json.dumps(data.get("result", {}), indent=2)[:500]}')

print('\n=== FIN DE PRUEBA ===')
