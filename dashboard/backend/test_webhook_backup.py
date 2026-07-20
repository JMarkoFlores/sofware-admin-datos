"""
Script de diagnóstico COMPLETO para el webhook RESUELVE BACKUP.
Simula exactamente el payload que Evolution API envía al webhook.
"""
import requests
import json

BACKEND_URL = "http://localhost:5000"
NUMERO_DESTINO = "51964253176"  # El número configurado en el sistema

print("=" * 60)
print("  DIAGNÓSTICO COMPLETO - RESUELVE BACKUP")
print("=" * 60)

# ── 1. Health check ──────────────────────────────────────────
print("\n[1] Health check del backend...")
try:
    r = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    print(f"    Status: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"    ERROR: Backend no responde - {e}")
    exit(1)

# ── 2. Estado del monitoreo de backup ────────────────────────
print("\n[2] Estado del monitoreo de backup...")
try:
    r = requests.get(f"{BACKEND_URL}/api/backup/status", timeout=5)
    data = r.json()
    print(f"    is_running:   {data.get('is_running')}")
    print(f"    destination:  {data.get('destination')}")
    print(f"    last_check:   {data.get('last_check')}")
    print(f"    last_result:  {data.get('last_result')}")
    backup_dest = data.get('destination', '')
    print(f"\n    >>> NÚMERO CONFIGURADO EN SISTEMA: '{backup_dest}'")
    print(f"    >>> NÚMERO QUE USAREMOS EN WEBHOOK: '{NUMERO_DESTINO}'")
    if backup_dest != NUMERO_DESTINO:
        print(f"    *** ADVERTENCIA: Los números NO coinciden exactamente! ***")
        print(f"    *** Esto causaría 'Número no autorizado' ***")
    else:
        print(f"    OK: Números coinciden.")
except Exception as e:
    print(f"    ERROR: {e}")

# ── 3. Simular webhook con payload de Evolution API ──────────
print("\n[3] Enviando webhook simulado con 'RESUELVE BACKUP'...")

# Payload que Evolution API envía cuando alguien escribe un mensaje
payload = {
    "event": "messages.upsert",
    "instance": "jean",
    "data": {
        "key": {
            "remoteJid": f"{NUMERO_DESTINO}@s.whatsapp.net",
            "fromMe": False,
            "id": "TEST_MSG_001"
        },
        "pushName": "Usuario Test",
        "status": "DELIVERY_ACK",
        "message": {
            "conversation": "RESUELVE BACKUP"
        },
        "messageType": "conversation",
        "messageTimestamp": 1234567890,
        "instanceId": "test-instance",
        "source": "android"
    }
}

print(f"    Payload enviado:")
print(f"    {json.dumps(payload, indent=4)}")

try:
    r = requests.post(
        f"{BACKEND_URL}/api/backup/webhook",
        json=payload,
        timeout=120  # El backup puede tardar
    )
    print(f"\n    HTTP Status: {r.status_code}")
    try:
        resp = r.json()
        print(f"    Respuesta: {json.dumps(resp, indent=4, ensure_ascii=False)}")
    except:
        print(f"    Respuesta raw: {r.text}")
except Exception as e:
    print(f"    ERROR al llamar webhook: {e}")

# ── 4. Usar endpoint de simulación alternativo ───────────────
print("\n[4] Usando endpoint /api/reports/simulate-incoming...")
try:
    r = requests.post(
        f"{BACKEND_URL}/api/reports/simulate-incoming",
        json={"number": NUMERO_DESTINO, "text": "RESUELVE BACKUP"},
        timeout=120
    )
    print(f"    HTTP Status: {r.status_code}")
    try:
        resp = r.json()
        print(f"    Respuesta: {json.dumps(resp, indent=4, ensure_ascii=False)}")
    except:
        print(f"    Respuesta raw: {r.text}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 60)
print("  DIAGNÓSTICO COMPLETADO - Revisa la consola de Flask")
print("  para ver los [DEBUG] logs detallados.")
print("=" * 60)
