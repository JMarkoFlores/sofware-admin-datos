"""
Helpers y utilidades comunes del backend.
"""

from flask import has_app_context
from models import Auditoria, db


def log_auditoria(tipo_operacion, modulo, descripcion, usuario='sistema', resultado='Éxito', detalle=None):
    """
    Registra una operación en la tabla de auditoría.
    Si no hay contexto activo de Flask, la omite en lugar de romper
    el flujo de reportes o WhatsApp.
    """
    if not has_app_context():
        print(f"[WARN AUDITORIA] Sin contexto de Flask, se omite registro: {descripcion}")
        return

    try:
        registro = Auditoria(
            tipo_operacion=tipo_operacion,
            modulo=modulo,
            descripcion=descripcion,
            usuario=usuario,
            resultado=resultado,
            detalle=detalle
        )
        db.session.add(registro)
        db.session.commit()
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f"[ERROR AUDITORIA] No se pudo registrar: {e}")
