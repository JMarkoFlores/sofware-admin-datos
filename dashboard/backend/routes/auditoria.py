from flask import Blueprint, jsonify, request
from models import Auditoria, db

bp = Blueprint('auditoria', __name__, url_prefix='/api/auditoria')


@bp.route('', methods=['GET'])
def get_auditoria():
    query = db.session.query(Auditoria)
    modulo = request.args.get('modulo')
    usuario = request.args.get('usuario')
    if modulo:
        query = query.filter(Auditoria.modulo.ilike(f'%{modulo}%'))
    if usuario:
        query = query.filter(Auditoria.usuario.ilike(f'%{usuario}%'))
    registros = query.order_by(Auditoria.fecha_hora.desc()).all()
    return jsonify([r.to_dict() for r in registros])


@bp.route('/<int:id>', methods=['GET'])
def get_registro(id):
    registro = db.session.get(Auditoria, id)
    if not registro:
        return jsonify({'error': 'Registro no encontrado'}), 404
    return jsonify(registro.to_dict())
