from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from models import UsuarioSistema, db
from utils.helpers import log_auditoria

bp = Blueprint('usuarios_sistema', __name__, url_prefix='/api/usuarios')


@bp.route('', methods=['GET'])
def get_usuarios():
    usuarios = db.session.query(UsuarioSistema).all()
    return jsonify([u.to_dict() for u in usuarios])


@bp.route('/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario = db.session.get(UsuarioSistema, id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario.to_dict())


@bp.route('', methods=['POST'])
def create_usuario():
    data = request.get_json()
    usuario = UsuarioSistema(
        username=data.get('username'),
        password_hash=generate_password_hash(data.get('password', 'password123')),
        nombre_completo=data.get('nombre_completo'),
        rol=data.get('rol', 'bibliotecario'),
        activo=data.get('activo', True)
    )
    db.session.add(usuario)
    db.session.commit()
    log_auditoria('CREATE', 'UsuariosSistema', f'Registro de nuevo usuario: {usuario.username}', detalle=f'Usuario ID {usuario.id}')
    return jsonify(usuario.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_usuario(id):
    usuario = db.session.get(UsuarioSistema, id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    data = request.get_json()
    usuario.username = data.get('username', usuario.username)
    if data.get('password'):
        usuario.password_hash = generate_password_hash(data.get('password'))
    usuario.nombre_completo = data.get('nombre_completo', usuario.nombre_completo)
    usuario.rol = data.get('rol', usuario.rol)
    usuario.activo = data.get('activo', usuario.activo)
    db.session.commit()
    log_auditoria('UPDATE', 'UsuariosSistema', f'Actualización de usuario: {usuario.username}', detalle=f'Usuario ID {usuario.id}')
    return jsonify(usuario.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = db.session.get(UsuarioSistema, id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    db.session.delete(usuario)
    db.session.commit()
    log_auditoria('DELETE', 'UsuariosSistema', f'Eliminación de usuario: {usuario.username}', detalle=f'Usuario ID {usuario.id}')
    return jsonify({'message': 'Usuario eliminado'})
