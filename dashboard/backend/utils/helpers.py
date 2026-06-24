"""
Helpers y utilidades comunes del backend.
"""

from models import Auditoria, db


def log_auditoria(tipo_operacion, modulo, descripcion, usuario='sistema', resultado='Éxito', detalle=None):
    """
    Registra una operación en la tabla de auditoría.
    """
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
        db.session.rollback()
        print(f"[ERROR AUDITORIA] No se pudo registrar: {e}")
