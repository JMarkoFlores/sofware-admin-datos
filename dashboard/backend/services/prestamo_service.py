"""
Servicio de lógica de negocio para Préstamos.
"""

from datetime import datetime
from models import Prestamo, Libro, db


def registrar_devolucion(prestamo_id, observaciones=None):
    prestamo = db.session.get(Prestamo, prestamo_id)
    if not prestamo:
        return False, 'Préstamo no encontrado'
    if prestamo.estado != 'activo':
        return False, 'El préstamo ya fue devuelto o está vencido'

    prestamo.estado = 'devuelto'
    prestamo.fecha_devolucion_real = datetime.now()
    if observaciones:
        prestamo.observaciones = observaciones

    libro = db.session.get(Libro, prestamo.libro_id)
    if libro:
        libro.ejemplares_disponibles += 1

    db.session.commit()
    return True, prestamo
