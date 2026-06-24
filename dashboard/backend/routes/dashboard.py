from flask import Blueprint, jsonify
from sqlalchemy import func
from models import Autor, Categoria, Libro, Lector, Prestamo, Multa, UsuarioSistema, Auditoria, db

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@bp.route('', methods=['GET'])
def get_dashboard():
    total_libros = db.session.query(Libro).count()
    total_autores = db.session.query(Autor).count()
    total_categorias = db.session.query(Categoria).count()
    total_lectores = db.session.query(Lector).count()
    prestamos_activos = db.session.query(Prestamo).filter_by(estado='activo').count()
    prestamos_vencidos = db.session.query(Prestamo).filter_by(estado='vencido').count()
    multas_pendientes = db.session.query(Multa).filter_by(pagada=False).count()
    total_usuarios = db.session.query(UsuarioSistema).count()
    ultima_auditoria = db.session.query(Auditoria).order_by(Auditoria.fecha_hora.desc()).first()

    return jsonify({
        'total_libros': total_libros,
        'total_autores': total_autores,
        'total_categorias': total_categorias,
        'total_lectores': total_lectores,
        'prestamos_activos': prestamos_activos,
        'prestamos_vencidos': prestamos_vencidos,
        'multas_pendientes': multas_pendientes,
        'total_usuarios': total_usuarios,
        'ultima_actividad': ultima_auditoria.to_dict() if ultima_auditoria else None,
    })
