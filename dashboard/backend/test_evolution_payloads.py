import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_URL = os.getenv('EVOLUTION_URL', 'http://localhost:8081')
API_KEY = os.getenv('EVOLUTION_API_KEY', 'mi-api-key-secreta-123')
INSTANCE = os.getenv('EVOLUTION_INSTANCE', 'mi-whatsapp')
DESTINATION = os.getenv('WHATSAPP_DESTINATION', '51964253176')

print(f"Testing with: {EVOLUTION_URL}, instance: {INSTANCE}, dest: {DESTINATION}")

# Test payloads
payloads = [
    # 1. Nested mediaMessage
    {
        "number": DESTINATION,
        "mediaMessage": {
            "mediatype": "document",
            "media": "SGVsbG8gV29ybGQh",  # "Hello World!" base64
            "fileName": "test.txt"
        }
    },
    # 2. Top-level fields
    {
        "number": DESTINATION,
        "mediatype": "document",
        "media": "SGVsbG8gV29ybGQh",
        "fileName": "test.txt"
    },
    # 3. mediaType camelCase
    {
        "number": DESTINATION,
        "mediaType": "document",
        "media": "SGVsbG8gV29ybGQh",
        "fileName": "test.txt"
    },
    # 4. Nested with mediaType camelCase
    {
        "number": DESTINATION,
        "mediaMessage": {
            "mediaType": "document",
            "media": "SGVsbG8gV29ybGQh",
            "fileName": "test.txt"
        }
    }
]

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

for i, payload in enumerate(payloads):
    print(f"\n=== Testing payload {i+1} ===")
    print(payload)
    url = f"{EVOLUTION_URL}/message/sendMedia/{INSTANCE}"
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
