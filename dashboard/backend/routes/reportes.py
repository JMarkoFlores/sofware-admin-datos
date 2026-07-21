from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models import Prestamo, Multa, Libro, Lector, db
from services.reporte_service import generar_reporte

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


@bp.route('/generar', methods=['POST'])
def generar_reporte_pdf():
    """
    Genera un reporte PDF con parámetros opcionales.
    
    Body JSON:
    {
        "tipo": "estadisticas|libros_prestados|multas|devoluciones_pendientes|libros_danios",
        "limit": 20,  // Opcional, para libros_prestados, multas, devoluciones_pendientes
        "dias": 30     // Opcional, para libros_danios
    }
    """
    data = request.get_json() or {}
    tipo = data.get('tipo')
    
    if not tipo:
        return jsonify({'exito': False, 'mensaje': 'Se requiere el tipo de reporte'}), 400
    
    # Validar tipo de reporte
    tipos_validos = ['estadisticas', 'libros_prestados', 'multas', 'devoluciones_pendientes', 'libros_danios']
    if tipo not in tipos_validos:
        return jsonify({'exito': False, 'mensaje': f'Tipo de reporte inválido. Debe ser uno de: {", ".join(tipos_validos)}'}), 400
    
    # Extraer parámetros opcionales
    params = {}
    if 'limit' in data:
        try:
            limit = int(data['limit'])
            if 1 <= limit <= 100:
                params['limit'] = limit
            else:
                return jsonify({'exito': False, 'mensaje': 'El parámetro limit debe estar entre 1 y 100'}), 400
        except ValueError:
            return jsonify({'exito': False, 'mensaje': 'El parámetro limit debe ser un número entero'}), 400
    
    if 'dias' in data:
        try:
            dias = int(data['dias'])
            if 1 <= dias <= 365:
                params['dias'] = dias
            else:
                return jsonify({'exito': False, 'mensaje': 'El parámetro dias debe estar entre 1 y 365'}), 400
        except ValueError:
            return jsonify({'exito': False, 'mensaje': 'El parámetro dias debe ser un número entero'}), 400
    
    # Generar reporte
    resultado = generar_reporte(tipo, **params)
    
    if resultado.get('exito'):
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 500
