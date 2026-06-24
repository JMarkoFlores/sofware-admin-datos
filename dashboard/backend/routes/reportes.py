from flask import Blueprint, jsonify
from sqlalchemy import func
from models import Prestamo, Multa, Libro, Lector, db

bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


@bp.route('/prestamos-activos', methods=['GET'])
def reporte_prestamos_activos():
    total = db.session.query(Prestamo).filter_by(estado='activo').count()
    return jsonify({'total_prestamos_activos': total})


@bp.route('/multas-pendientes', methods=['GET'])
def reporte_multas_pendientes():
    total = db.session.query(Multa).filter_by(pagada=False).count()
    monto = db.session.query(func.sum(Multa.monto)).filter_by(pagada=False).scalar() or 0
    return jsonify({'total_multas_pendientes': total, 'monto_total': float(monto)})


@bp.route('/libros-mas-prestados', methods=['GET'])
def reporte_libros_mas_prestados():
    from sqlalchemy import desc
    resultados = (
        db.session.query(Libro.titulo, func.count(Prestamo.id).label('total'))
        .join(Prestamo, Libro.id == Prestamo.libro_id)
        .group_by(Libro.id, Libro.titulo)
        .order_by(desc('total'))
        .limit(5)
        .all()
    )
    return jsonify([{'titulo': r.titulo, 'total': r.total} for r in resultados])


@bp.route('/lectores-con-multas', methods=['GET'])
def reporte_lectores_con_multas():
    from sqlalchemy import desc
    resultados = (
        db.session.query(Lector.nombres, Lector.apellidos, func.count(Multa.id).label('total'))
        .join(Multa, Lector.id == Multa.lector_id)
        .filter(Multa.pagada == False)
        .group_by(Lector.id, Lector.nombres, Lector.apellidos)
        .order_by(desc('total'))
        .all()
    )
    return jsonify([{'lector': f"{r.nombres} {r.apellidos}", 'multas': r.total} for r in resultados])
