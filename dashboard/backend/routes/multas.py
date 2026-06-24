from datetime import datetime
from flask import Blueprint, jsonify, request
from models import Multa, db
from utils.helpers import log_auditoria

bp = Blueprint('multas', __name__, url_prefix='/api/multas')


@bp.route('', methods=['GET'])
def get_multas():
    multas = db.session.query(Multa).all()
    return jsonify([m.to_dict() for m in multas])


@bp.route('/<int:id>', methods=['GET'])
def get_multa(id):
    multa = db.session.get(Multa, id)
    if not multa:
        return jsonify({'error': 'Multa no encontrada'}), 404
    return jsonify(multa.to_dict())


@bp.route('', methods=['POST'])
def create_multa():
    data = request.get_json()
    multa = Multa(
        lector_id=data.get('lector_id'),
        prestamo_id=data.get('prestamo_id'),
        monto=data.get('monto'),
        motivo=data.get('motivo'),
        pagada=data.get('pagada', False)
    )
    db.session.add(multa)
    db.session.commit()
    log_auditoria('CREATE', 'Multas', f'Registro de nueva multa: {multa.monto}', detalle=f'Multa ID {multa.id}')
    return jsonify(multa.to_dict()), 201


@bp.route('/<int:id>/pagar', methods=['PUT'])
def pagar_multa(id):
    multa = db.session.get(Multa, id)
    if not multa:
        return jsonify({'error': 'Multa no encontrada'}), 404
    if multa.pagada:
        return jsonify({'error': 'La multa ya está pagada'}), 400
    multa.pagada = True
    multa.fecha_pago = datetime.now()
    db.session.commit()
    log_auditoria('UPDATE', 'Multas', f'Pago de multa: {multa.monto}', detalle=f'Multa ID {multa.id}')
    return jsonify(multa.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_multa(id):
    multa = db.session.get(Multa, id)
    if not multa:
        return jsonify({'error': 'Multa no encontrada'}), 404
    db.session.delete(multa)
    db.session.commit()
    log_auditoria('DELETE', 'Multas', f'Eliminación de multa: {multa.monto}', detalle=f'Multa ID {multa.id}')
    return jsonify({'message': 'Multa eliminada'})
