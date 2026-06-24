"""
Servicio de lógica de negocio para Libros.
"""

from models import Libro, db


def verificar_disponibilidad(libro_id):
    libro = db.session.get(Libro, libro_id)
    if not libro:
        return False, 'Libro no encontrado'
    if libro.ejemplares_disponibles <= 0:
        return False, 'No hay ejemplares disponibles'
    return True, libro
