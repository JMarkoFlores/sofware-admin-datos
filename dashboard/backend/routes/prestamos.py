from datetime import datetime
from flask import Blueprint, jsonify, request
from models import Prestamo, Libro, db
from utils.helpers import log_auditoria

bp = Blueprint('prestamos', __name__, url_prefix='/api/prestamos')


@bp.route('', methods=['GET'])
def get_prestamos():
    prestamos = db.session.query(Prestamo).all()
    return jsonify([p.to_dict() for p in prestamos])


@bp.route('/<int:id>', methods=['GET'])
def get_prestamo(id):
    prestamo = db.session.get(Prestamo, id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    return jsonify(prestamo.to_dict())


@bp.route('', methods=['POST'])
def create_prestamo():
    data = request.get_json()
    libro = db.session.get(Libro, data.get('libro_id'))
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    if libro.ejemplares_disponibles <= 0:
        return jsonify({'error': 'No hay ejemplares disponibles'}), 400

    prestamo = Prestamo(
        lector_id=data.get('lector_id'),
        libro_id=data.get('libro_id'),
        fecha_devolucion_esperada=data.get('fecha_devolucion_esperada'),
        observaciones=data.get('observaciones')
    )
    libro.ejemplares_disponibles -= 1
    db.session.add(prestamo)
    db.session.commit()
    log_auditoria('CREATE', 'Prestamos', f'Registro de nuevo préstamo: ID {prestamo.id}', detalle=f'Préstamo ID {prestamo.id}')
    return jsonify(prestamo.to_dict()), 201


@bp.route('/<int:id>/devolver', methods=['PUT'])
def devolver_prestamo(id):
    prestamo = db.session.get(Prestamo, id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    if prestamo.estado != 'activo':
        return jsonify({'error': 'El préstamo ya fue devuelto o está vencido'}), 400

    data = request.get_json() or {}
    prestamo.estado = 'devuelto'
    prestamo.fecha_devolucion_real = datetime.now()
    prestamo.observaciones = data.get('observaciones', prestamo.observaciones)

    libro = db.session.get(Libro, prestamo.libro_id)
    if libro:
        libro.ejemplares_disponibles += 1

    db.session.commit()
    log_auditoria('UPDATE', 'Prestamos', f'Devolución de préstamo: ID {prestamo.id}', detalle=f'Préstamo ID {prestamo.id}')
    return jsonify(prestamo.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_prestamo(id):
    prestamo = db.session.get(Prestamo, id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    db.session.delete(prestamo)
    db.session.commit()
    log_auditoria('DELETE', 'Prestamos', f'Eliminación de préstamo: ID {prestamo.id}', detalle=f'Préstamo ID {prestamo.id}')
    return jsonify({'message': 'Préstamo eliminado'})
