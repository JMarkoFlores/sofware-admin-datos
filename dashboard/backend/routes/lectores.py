from flask import Blueprint, jsonify, request
from models import Lector, db
from utils.helpers import log_auditoria

bp = Blueprint('lectores', __name__, url_prefix='/api/lectores')


@bp.route('', methods=['GET'])
def get_lectores():
    lectores = db.session.query(Lector).all()
    return jsonify([l.to_dict() for l in lectores])


@bp.route('/<int:id>', methods=['GET'])
def get_lector(id):
    lector = db.session.get(Lector, id)
    if not lector:
        return jsonify({'error': 'Lector no encontrado'}), 404
    return jsonify(lector.to_dict())


@bp.route('', methods=['POST'])
def create_lector():
    data = request.get_json()
    lector = Lector(
        codigo_estudiante=data.get('codigo_estudiante'),
        nombres=data.get('nombres'),
        apellidos=data.get('apellidos'),
        email=data.get('email'),
        telefono=data.get('telefono'),
        carrera=data.get('carrera'),
        facultad=data.get('facultad'),
        activo=data.get('activo', True)
    )
    db.session.add(lector)
    db.session.commit()
    log_auditoria('CREATE', 'Lectores', f'Registro de nuevo lector: {lector.nombres}', detalle=f'Lector ID {lector.id}')
    return jsonify(lector.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_lector(id):
    lector = db.session.get(Lector, id)
    if not lector:
        return jsonify({'error': 'Lector no encontrado'}), 404
    data = request.get_json()
    lector.codigo_estudiante = data.get('codigo_estudiante', lector.codigo_estudiante)
    lector.nombres = data.get('nombres', lector.nombres)
    lector.apellidos = data.get('apellidos', lector.apellidos)
    lector.email = data.get('email', lector.email)
    lector.telefono = data.get('telefono', lector.telefono)
    lector.carrera = data.get('carrera', lector.carrera)
    lector.facultad = data.get('facultad', lector.facultad)
    lector.activo = data.get('activo', lector.activo)
    db.session.commit()
    log_auditoria('UPDATE', 'Lectores', f'Actualización de lector: {lector.nombres}', detalle=f'Lector ID {lector.id}')
    return jsonify(lector.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_lector(id):
    lector = db.session.get(Lector, id)
    if not lector:
        return jsonify({'error': 'Lector no encontrado'}), 404
    db.session.delete(lector)
    db.session.commit()
    log_auditoria('DELETE', 'Lectores', f'Eliminación de lector: {lector.nombres}', detalle=f'Lector ID {lector.id}')
    return jsonify({'message': 'Lector eliminado'})
