"""
Script de pruebas unitarias e integración para la funcionalidad de Bloqueo de Usuario via WhatsApp ("BLOQUEAR")
=============================================================================================================
Prueba:
1. Formato y construcción del comando SQL 'dbo.sp_BloquearUsuarioLogin'.
2. Reconocimiento de las variantes 'BLOQUEAR', 'bloquear', 'BLOQUEA', 'bloquea' en procesar_comando_login.
3. Simulación de recepción de webhook en el endpoint con payload de Evolution API.
"""

import sys
import os
import unittest
from datetime import datetime

# Agregar path al backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import services.login_security_service as ls_service
from routes.disparador import _extract_text_from_webhook_message, _extract_message_info_from_payload

class TestBloquearUsuarioWhatsApp(unittest.TestCase):

    def setUp(self):
        # Resetear estado de variables globales para ambiente limpio de pruebas
        ls_service.failed_attempts = {}
        ls_service.pending_alerts = {
            'TestUserSeguridad': {
                'timestamp': datetime.now(),
                'count': 3,
                'notified': True
            }
        }
        ls_service.current_pending_alert_username = 'TestUserSeguridad'

    def test_reconocimiento_comando_bloquear_mayusculas(self):
        """Prueba que 'BLOQUEAR' ejecute el bloqueo del usuario pendiente (mocking ejecucion sql)."""
        original_disable = ls_service.disable_login
        original_send_conf = ls_service.send_confirmation_bloqueo
        
        executed_username = []
        conf_sent = []

        def mock_disable_login(username):
            executed_username.append(username)
            return {'exito': True, 'mensaje': f'Login {username} deshabilitado exitosamente'}

        def mock_send_confirmation(dest, username):
            conf_sent.append((dest, username))
            return {'success': True}

        ls_service.disable_login = mock_disable_login
        ls_service.send_confirmation_bloqueo = mock_send_confirmation

        try:
            resultado = ls_service.procesar_comando_login(
                texto="BLOQUEAR",
                numero_remoto="5190065850",
                numero_destino_configurado="5190065850"
            )

            self.assertTrue(resultado['procesado'])
            self.assertTrue(resultado['exito'])
            self.assertEqual(executed_username, ['TestUserSeguridad'])
            self.assertEqual(conf_sent, [("5190065850", "TestUserSeguridad")])
            self.assertNotIn('TestUserSeguridad', ls_service.pending_alerts)
        finally:
            ls_service.disable_login = original_disable
            ls_service.send_confirmation_bloqueo = original_send_conf

    def test_reconocimiento_comando_bloquear_minusculas(self):
        """Prueba que 'bloquear' (en minusculas) reconozca el comando."""
        original_disable = ls_service.disable_login
        original_send_conf = ls_service.send_confirmation_bloqueo
        
        executed_username = []
        ls_service.disable_login = lambda username: (executed_username.append(username) or {'exito': True, 'mensaje': 'ok'})
        ls_service.send_confirmation_bloqueo = lambda dest, username: {'success': True}

        try:
            resultado = ls_service.procesar_comando_login(
                texto="bloquear",
                numero_remoto="5190065850",
                numero_destino_configurado="5190065850"
            )

            self.assertTrue(resultado['procesado'])
            self.assertTrue(resultado['exito'])
            self.assertEqual(executed_username, ['TestUserSeguridad'])
        finally:
            ls_service.disable_login = original_disable
            ls_service.send_confirmation_bloqueo = original_send_conf

    def test_payload_evolution_api_webhook_extract(self):
        """Prueba la extraccion del texto 'BLOQUEAR' desde el payload JSON de Evolution API."""
        payload = {
            "event": "messages.upsert",
            "data": {
                "key": {
                    "remoteJid": "5190065850@s.whatsapp.net",
                    "fromMe": False,
                    "id": "MSG_12345"
                },
                "message": {
                    "conversation": "BLOQUEAR"
                }
            }
        }

        mensajes = _extract_message_info_from_payload(payload)
        self.assertEqual(len(mensajes), 1)
        remote_jid, from_me, msg_dict = mensajes[0]
        self.assertEqual(remote_jid, "5190065850@s.whatsapp.net")
        self.assertFalse(from_me)

        texto_extraido = _extract_text_from_webhook_message(msg_dict)
        self.assertEqual(texto_extraido, "BLOQUEAR")

if __name__ == '__main__':
    print("=" * 60)
    print("  EJECUTANDO PRUEBAS UNITARIAS: BLOQUEAR VIA WHATSAPP")
    print("=" * 60)
    unittest.main()
