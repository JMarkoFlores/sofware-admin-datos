import requests
import json

headers = {'apikey': 'mi-api-key-secreta-123'}

print('=== VERIFICANDO EVOLUTION API ===')

# 1. Listar instancias
r = requests.get('http://localhost:8080/instance/fetchInstances', headers=headers)
print(f'\n1. Instancias disponibles:')
if r.status_code == 200:
    instances = r.json()
    if instances:
        for inst in instances:
            name = inst['name']
            status = inst.get('connectionStatus', 'N/A')
            print(f'   - {name}: {status}')
    else:
        print('   Ninguna instancia encontrada')
else:
    print(f'   Error {r.status_code}: {r.text[:200]}')

# 2. Verificar estado de mi-whatsapp
print('\n2. Estado de mi-whatsapp:')
r = requests.get('http://localhost:8080/instance/connectionState/mi-whatsapp', headers=headers)
print(f'   Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'   Respuesta: {json.dumps(data, indent=2)}')
else:
    print(f'   Error: {r.text[:500]}')

# 3. Probar envio directo
print('\n3. Prueba de envio directo:')
url = 'http://localhost:8080/message/sendText/mi-whatsapp'
payload = {'number': '51952310138', 'text': 'Mensaje de prueba'}
r = requests.post(url, headers={**headers, 'Content-Type': 'application/json'}, json=payload)
print(f'   Status: {r.status_code}')
print(f'   Respuesta: {r.text[:500]}')

print('\n=== DIAGNOSTICO ===')
if r.status_code == 404:
    print('ERROR 404: La instancia "mi-whatsapp" no existe o no esta conectada.')
    print('Solucion: Conectar WhatsApp en http://localhost:8080/manager')
elif r.status_code == 201:
    print('OK: El envio funciona correctamente.')
else:
    print(f'Error inesperado: {r.status_code}')
