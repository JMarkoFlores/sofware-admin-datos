from flask import Blueprint, jsonify, request
from models import Autor, db
from utils.helpers import log_auditoria

bp = Blueprint('autores', __name__, url_prefix='/api/autores')


@bp.route('', methods=['GET'])
def get_autores():
    autores = db.session.query(Autor).all()
    return jsonify([a.to_dict() for a in autores])


@bp.route('/<int:id>', methods=['GET'])
def get_autor(id):
    autor = db.session.get(Autor, id)
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    return jsonify(autor.to_dict())


@bp.route('', methods=['POST'])
def create_autor():
    data = request.get_json()
    autor = Autor(
        nombre=data.get('nombre'),
        apellido=data.get('apellido'),
        nacionalidad=data.get('nacionalidad'),
        fecha_nacimiento=data.get('fecha_nacimiento'),
        biografia=data.get('biografia')
    )
    db.session.add(autor)
    db.session.commit()
    log_auditoria('CREATE', 'Autores', f'Registro de nuevo autor: {autor.nombre}', detalle=f'Autor ID {autor.id}')
    return jsonify(autor.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_autor(id):
    autor = db.session.get(Autor, id)
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    data = request.get_json()
    autor.nombre = data.get('nombre', autor.nombre)
    autor.apellido = data.get('apellido', autor.apellido)
    autor.nacionalidad = data.get('nacionalidad', autor.nacionalidad)
    autor.fecha_nacimiento = data.get('fecha_nacimiento', autor.fecha_nacimiento)
    autor.biografia = data.get('biografia', autor.biografia)
    db.session.commit()
    log_auditoria('UPDATE', 'Autores', f'Actualización de autor: {autor.nombre}', detalle=f'Autor ID {autor.id}')
    return jsonify(autor.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_autor(id):
    autor = db.session.get(Autor, id)
    if not autor:
        return jsonify({'error': 'Autor no encontrado'}), 404
    db.session.delete(autor)
    db.session.commit()
    log_auditoria('DELETE', 'Autores', f'Eliminación de autor: {autor.nombre}', detalle=f'Autor ID {autor.id}')
    return jsonify({'message': 'Autor eliminado'})
