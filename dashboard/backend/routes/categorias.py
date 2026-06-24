from flask import Blueprint, jsonify, request
from models import Categoria, db
from utils.helpers import log_auditoria

bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')


@bp.route('', methods=['GET'])
def get_categorias():
    categorias = db.session.query(Categoria).all()
    return jsonify([c.to_dict() for c in categorias])


@bp.route('/<int:id>', methods=['GET'])
def get_categoria(id):
    categoria = db.session.get(Categoria, id)
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    return jsonify(categoria.to_dict())


@bp.route('', methods=['POST'])
def create_categoria():
    data = request.get_json()
    categoria = Categoria(
        nombre=data.get('nombre'),
        descripcion=data.get('descripcion')
    )
    db.session.add(categoria)
    db.session.commit()
    log_auditoria('CREATE', 'Categorias', f'Registro de nueva categoría: {categoria.nombre}', detalle=f'Categoría ID {categoria.id}')
    return jsonify(categoria.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_categoria(id):
    categoria = db.session.get(Categoria, id)
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    data = request.get_json()
    categoria.nombre = data.get('nombre', categoria.nombre)
    categoria.descripcion = data.get('descripcion', categoria.descripcion)
    db.session.commit()
    log_auditoria('UPDATE', 'Categorias', f'Actualización de categoría: {categoria.nombre}', detalle=f'Categoría ID {categoria.id}')
    return jsonify(categoria.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_categoria(id):
    categoria = db.session.get(Categoria, id)
    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    db.session.delete(categoria)
    db.session.commit()
    log_auditoria('DELETE', 'Categorias', f'Eliminación de categoría: {categoria.nombre}', detalle=f'Categoría ID {categoria.id}')
    return jsonify({'message': 'Categoría eliminada'})
