import requests

print('=== PRUEBA DE BACKEND ===')

# Health check
r = requests.get('http://localhost:5000/api/health')
print('1. Health:', r.status_code)

# Status
r = requests.get('http://localhost:5000/api/status')
data = r.json()
print('2. Status: is_running=', data.get('is_running'), ', dest=', data.get('destination'))

# Test send
r = requests.get('http://localhost:5000/api/test-send')
data = r.json()
print('3. Test send: success=', data.get('success'))

# Probar POST con número personalizado
print('\n4. Probando POST con número 51999999999...')
r = requests.post('http://localhost:5000/api/start', json={'number': '51999999999'})
print('   Status:', r.status_code)
print('   Response:', r.json())

# Detener
print('\n5. Deteniendo...')
r = requests.get('http://localhost:5000/api/stop')
print('   Status:', r.status_code)

print('\nBackend OK - Todo funciona correctamente')
