#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whatsapp import send_message

print("Testing send_message directly...")
result = send_message("Prueba desde test script", "51940967068")
print(f"Result: {result}")
