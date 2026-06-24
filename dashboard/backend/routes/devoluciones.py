from flask import Blueprint, jsonify, request
from models import Devolucion, db
from utils.helpers import log_auditoria

bp = Blueprint('devoluciones', __name__, url_prefix='/api/devoluciones')


@bp.route('', methods=['GET'])
def get_devoluciones():
    devoluciones = db.session.query(Devolucion).all()
    return jsonify([d.to_dict() for d in devoluciones])


@bp.route('/<int:id>', methods=['GET'])
def get_devolucion(id):
    devolucion = db.session.get(Devolucion, id)
    if not devolucion:
        return jsonify({'error': 'Devolución no encontrada'}), 404
    return jsonify(devolucion.to_dict())


@bp.route('', methods=['POST'])
def create_devolucion():
    data = request.get_json()
    devolucion = Devolucion(
        prestamo_id=data.get('prestamo_id'),
        estado_libro=data.get('estado_libro', 'bueno'),
        observaciones=data.get('observaciones')
    )
    db.session.add(devolucion)
    db.session.commit()
    log_auditoria('CREATE', 'Devoluciones', f'Registro de nueva devolución: ID {devolucion.id}', detalle=f'Devolución ID {devolucion.id}')
    return jsonify(devolucion.to_dict()), 201


@bp.route('/<int:id>', methods=['DELETE'])
def delete_devolucion(id):
    devolucion = db.session.get(Devolucion, id)
    if not devolucion:
        return jsonify({'error': 'Devolución no encontrada'}), 404
    db.session.delete(devolucion)
    db.session.commit()
    log_auditoria('DELETE', 'Devoluciones', f'Eliminación de devolución: ID {devolucion.id}', detalle=f'Devolución ID {devolucion.id}')
    return jsonify({'message': 'Devolución eliminada'})
