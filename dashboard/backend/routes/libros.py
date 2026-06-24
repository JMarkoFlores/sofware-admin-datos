from flask import Blueprint, jsonify, request
from models import Libro, db
from utils.helpers import log_auditoria

bp = Blueprint('libros', __name__, url_prefix='/api/libros')


@bp.route('', methods=['GET'])
def get_libros():
    libros = db.session.query(Libro).all()
    return jsonify([l.to_dict() for l in libros])


@bp.route('/<int:id>', methods=['GET'])
def get_libro(id):
    libro = db.session.get(Libro, id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    return jsonify(libro.to_dict())


@bp.route('', methods=['POST'])
def create_libro():
    data = request.get_json()
    libro = Libro(
        titulo=data.get('titulo'),
        isbn=data.get('isbn'),
        anio_publicacion=data.get('anio_publicacion'),
        editorial=data.get('editorial'),
        ejemplares_total=data.get('ejemplares_total', 1),
        ejemplares_disponibles=data.get('ejemplares_disponibles', data.get('ejemplares_total', 1)),
        autor_id=data.get('autor_id'),
        categoria_id=data.get('categoria_id')
    )
    db.session.add(libro)
    db.session.commit()
    log_auditoria('CREATE', 'Libros', f'Registro de nuevo libro: {libro.titulo}', detalle=f'Libro ID {libro.id}')
    return jsonify(libro.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_libro(id):
    libro = db.session.get(Libro, id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    data = request.get_json()
    libro.titulo = data.get('titulo', libro.titulo)
    libro.isbn = data.get('isbn', libro.isbn)
    libro.anio_publicacion = data.get('anio_publicacion', libro.anio_publicacion)
    libro.editorial = data.get('editorial', libro.editorial)
    libro.ejemplares_total = data.get('ejemplares_total', libro.ejemplares_total)
    libro.ejemplares_disponibles = data.get('ejemplares_disponibles', libro.ejemplares_disponibles)
    libro.autor_id = data.get('autor_id', libro.autor_id)
    libro.categoria_id = data.get('categoria_id', libro.categoria_id)
    db.session.commit()
    log_auditoria('UPDATE', 'Libros', f'Actualización de libro: {libro.titulo}', detalle=f'Libro ID {libro.id}')
    return jsonify(libro.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_libro(id):
    libro = db.session.get(Libro, id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    db.session.delete(libro)
    db.session.commit()
    log_auditoria('DELETE', 'Libros', f'Eliminación de libro: {libro.titulo}', detalle=f'Libro ID {libro.id}')
    return jsonify({'message': 'Libro eliminado'})
