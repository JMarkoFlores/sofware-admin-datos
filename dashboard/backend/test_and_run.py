import subprocess
import time
import requests
import json
import sys

print('=== INICIANDO BACKEND Y HACIENDO PRUEBAS ===')

# Iniciar backend en segundo plano
print('\n1. Iniciando backend Flask...')
backend_process = subprocess.Popen(
    [sys.executable, 'app.py'],
    cwd=r'C:\Users\jeanm\Downloads\Software-Datos\dashboard\backend',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

print(f'   PID: {backend_process.pid}')
print('   Esperando 5 segundos para que inicie...')
time.sleep(5)

BASE_URL = 'http://localhost:5000'

# Probar health
print('\n2. Health check...')
try:
    r = requests.get(f'{BASE_URL}/api/health', timeout=5)
    print(f'   OK - Status: {r.status_code}')
except Exception as e:
    print(f'   ERROR: {e}')

# Verificar estado
print('\n3. Estado...')
try:
    r = requests.get(f'{BASE_URL}/api/status', timeout=5)
    data = r.json()
    print(f'   is_running: {data.get("is_running")}')
    print(f'   last_message: {data.get("last_message")}')
except Exception as e:
    print(f'   ERROR: {e}')

# Obtener tablas
print('\n4. Obteniendo tablas...')
try:
    r = requests.get(f'{BASE_URL}/api/tables', timeout=10)
    data = r.json()
    print(f'   Tablas: {data.get("count")}')
    if data.get('error'):
        print(f'   ERROR DB: {data["error"]}')
except Exception as e:
    print(f'   ERROR: {e}')

# Prueba de envío
print('\n5. Enviando mensaje de prueba...')
try:
    r = requests.get(f'{BASE_URL}/api/test-send', timeout=15)
    data = r.json()
    print(f'   Status: {r.status_code}')
    print(f'   Success: {data.get("success")}')
    result = data.get('result', {})
    print(f'   Status Code: {result.get("status_code")}')
    if result.get('error'):
        print(f'   Error: {result["error"]}')
    print(f'   Mensaje: {data.get("message_sent", "N/A")[:100]}...')
except Exception as e:
    print(f'   ERROR: {e}')

print('\n=== PRUEBA COMPLETADA ===')
print('Presiona ENTER para detener el backend...')
input()

backend_process.terminate()
print('Backend detenido.')
