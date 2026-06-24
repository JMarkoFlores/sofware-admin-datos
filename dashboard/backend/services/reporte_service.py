"""
Servicio para generación de reportes.
"""

from sqlalchemy import func
from models import Prestamo, Multa, Libro, Lector, db


def libros_mas_prestados(limit=5):
    from sqlalchemy import desc
    return (
        db.session.query(Libro.titulo, func.count(Prestamo.id).label('total'))
        .join(Prestamo, Libro.id == Prestamo.libro_id)
        .group_by(Libro.id, Libro.titulo)
        .order_by(desc('total'))
        .limit(limit)
        .all()
    )
