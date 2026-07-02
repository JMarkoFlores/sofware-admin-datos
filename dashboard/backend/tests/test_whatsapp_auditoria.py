import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Auditoria, db
from services.reporte_service import generar_reporte
from whatsapp import send_message


@pytest.fixture()
def client():
    with app.app_context():
        yield app.test_client()


def test_send_message_creates_audit_record(monkeypatch):
    with app.app_context():
        before = db.session.query(Auditoria).count()

        class FakeResponse:
            status_code = 201
            text = 'ok'

            def json(self):
                return {'status': 'ok'}

        monkeypatch.setattr('whatsapp.requests.post', lambda *args, **kwargs: FakeResponse())
        send_message('Mensaje de prueba', '51999999999')

        after = db.session.query(Auditoria).count()
        assert after == before + 1

        last_record = db.session.query(Auditoria).order_by(Auditoria.id.desc()).first()
        assert last_record.modulo == 'WhatsApp'
        assert last_record.tipo_operacion == 'WHATSAPP'


def test_send_message_without_app_context_does_not_crash(monkeypatch):
    class FakeResponse:
        status_code = 201
        text = 'ok'

        def json(self):
            return {'status': 'ok'}

    monkeypatch.setattr('whatsapp.requests.post', lambda *args, **kwargs: FakeResponse())

    result = send_message('Mensaje de prueba fuera de contexto', '51999999999')

    assert result['success'] is True
    assert result['status_code'] == 201


def test_generar_reporte_creates_pdf_for_books(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv('REPORTS_OUTPUT_DIR', tmpdir)

        resultado = generar_reporte('libros_disponibles')

        assert resultado['exito'] is True
        assert resultado['pdf_path']
        assert os.path.exists(resultado['pdf_path'])
        assert resultado['pdf_path'].endswith('.pdf')
