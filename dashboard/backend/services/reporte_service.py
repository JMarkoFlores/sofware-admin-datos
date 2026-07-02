"""
Servicio para generación de reportes detallados en PDF para WhatsApp.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from flask import has_app_context
from sqlalchemy import desc, func
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models import Autor, Categoria, Devolucion, Libro, Lector, Multa, Prestamo, db

REPORTS_OUTPUT_DIR = os.getenv(
    'REPORTS_OUTPUT_DIR',
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
)


def _slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def _crear_pdf_reporte(titulo, contenido):
    output_dir = Path(REPORTS_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{_slugify(titulo)}_{timestamp}.pdf"
    file_path = output_dir / file_name

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=24
    )

    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    elements.extend(contenido)
    doc.build(elements)
    return str(file_path)


def _crear_tabla(datos, encabezados, anchos=None):
    table_data = [encabezados]
    table_data.extend(datos)
    
    if anchos is None:
        anchos = [None] * len(encabezados)
    
    table = Table(table_data, colWidths=anchos)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f1f5f9')]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])
    table.setStyle(style)
    return table


def libros_mas_prestados(limit=5):
    """Libros más prestados."""
    return (
        db.session.query(Libro.titulo, func.count(Prestamo.id).label('total'))
        .join(Prestamo, Libro.id == Prestamo.libro_id)
        .group_by(Libro.id, Libro.titulo)
        .order_by(desc('total'))
        .limit(limit)
        .all()
    )


def libros_disponibles(limit=20):
    """Lista detallada de libros disponibles."""
    return (
        db.session.query(Libro)
        .filter(Libro.ejemplares_disponibles > 0)
        .order_by(Libro.titulo)
        .limit(limit)
        .all()
    )


def lectores_activos(limit=20):
    """Lista detallada de lectores activos."""
    return (
        db.session.query(Lector)
        .filter(Lector.activo == True)
        .order_by(Lector.apellidos, Lector.nombres)
        .limit(limit)
        .all()
    )


def prestamos_activos(limit=20):
    """Detalle de préstamos activos."""
    return (
        db.session.query(Prestamo)
        .filter(Prestamo.estado == 'activo')
        .order_by(Prestamo.fecha_devolucion_esperada)
        .limit(limit)
        .all()
    )


def multas_pendientes(limit=20):
    """Detalle de multas pendientes."""
    return (
        db.session.query(Multa)
        .filter(Multa.pagada == False)
        .order_by(desc(Multa.monto))
        .limit(limit)
        .all()
    )


def prestamos_vencidos(limit=20):
    """Préstamos vencidos."""
    hoy = datetime.utcnow().date()
    return (
        db.session.query(Prestamo)
        .filter(
            Prestamo.estado == 'activo',
            Prestamo.fecha_devolucion_esperada < hoy
        )
        .order_by(desc(Prestamo.fecha_devolucion_esperada))
        .limit(limit)
        .all()
    )


def libros_dañados_recientes(dias=30):
    """Libros reportados como dañados en los últimos N días."""
    fecha_limite = datetime.utcnow() - timedelta(days=dias)
    return (
        db.session.query(
            Libro.titulo,
            func.count(Devolucion.id).label('total_danios')
        )
        .join(Devolucion, Devolucion.prestamo_id == Prestamo.id)
        .join(Prestamo, Prestamo.libro_id == Libro.id)
        .filter(
            Devolucion.estado_libro == 'dañado',
            Devolucion.created_at >= fecha_limite
        )
        .group_by(Libro.id, Libro.titulo)
        .order_by(desc('total_danios'))
        .all()
    )


def estadisticas_generales():
    """Estadísticas generales de la biblioteca."""
    total_libros = db.session.query(func.count(Libro.id)).scalar() or 0
    libros_disponibles_total = db.session.query(func.sum(Libro.ejemplares_disponibles)).scalar() or 0
    total_autores = db.session.query(func.count(Autor.id)).scalar() or 0
    total_categorias = db.session.query(func.count(Categoria.id)).scalar() or 0
    total_lectores = db.session.query(func.count(Lector.id)).scalar() or 0
    prestamos_total = db.session.query(func.count(Prestamo.id)).filter(Prestamo.estado == 'activo').scalar() or 0
    multas = {
        'cantidad': db.session.query(func.count(Multa.id)).filter(Multa.pagada == False).scalar() or 0,
        'monto_total': float(db.session.query(func.sum(Multa.monto)).filter(Multa.pagada == False).scalar() or 0)
    }
    return {
        'total_libros': total_libros,
        'libros_disponibles': libros_disponibles_total,
        'total_autores': total_autores,
        'total_categorias': total_categorias,
        'total_lectores': total_lectores,
        'prestamos_activos': prestamos_total,
        'multas_pendientes': multas['cantidad'],
        'monto_multas_pendientes': multas['monto_total']
    }


def _generar_pdf_por_tipo(report_type):
    if not has_app_context():
        raise RuntimeError('Se requiere un contexto de Flask para generar reportes PDF')

    if report_type == 'estadisticas':
        stats = estadisticas_generales()
        titulo = 'REPORTE GENERAL DE LA BIBLIOTECA'
        contenido = []
        datos_tabla = [
            ['Total de libros', str(stats['total_libros'])],
            ['Libros disponibles', str(stats['libros_disponibles'])],
            ['Autores', str(stats['total_autores'])],
            ['Categorías', str(stats['total_categorias'])],
            ['Lectores activos', str(stats['total_lectores'])],
            ['Préstamos activos', str(stats['prestamos_activos'])],
            ['Multas pendientes', str(stats['multas_pendientes'])],
            ['Monto total multas', f"S/. {stats['monto_multas_pendientes']:.2f}"]
        ]
        tabla = _crear_tabla(datos_tabla, ['Indicador', 'Valor'], [3*inch, 2*inch])
        contenido.append(tabla)
        return _crear_pdf_reporte(titulo, contenido), titulo, datos_tabla

    if report_type == 'libros_prestados':
        libros = libros_mas_prestados(20)
        titulo = 'REPORTE DE LIBROS MÁS PRESTADOS'
        contenido = []
        if libros:
            datos_tabla = [[libro.titulo, str(libro.total)] for libro in libros]
            tabla = _crear_tabla(datos_tabla, ['Título del Libro', 'Total Préstamos'], [4*inch, 1.5*inch])
            contenido.append(tabla)
        else:
            from reportlab.platypus import Paragraph
            styles = getSampleStyleSheet()
            contenido.append(Paragraph('No hay datos de préstamos para mostrar.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    if report_type == 'libros_disponibles':
        libros = libros_disponibles(20)
        titulo = 'REPORTE DE LIBROS DISPONIBLES'
        contenido = []
        if libros:
            datos_tabla = []
            for libro in libros:
                autor = libro.autor.nombre if libro.autor else 'Sin autor'
                categoria = libro.categoria.nombre if libro.categoria else 'Sin categoría'
                datos_tabla.append([
                    libro.titulo,
                    autor,
                    categoria,
                    f"{libro.ejemplares_disponibles}/{libro.ejemplares_total}"
                ])
            if datos_tabla:
                tabla = _crear_tabla(datos_tabla, ['Título', 'Autor', 'Categoría', 'Disponibles/Total'], [2.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
                contenido.append(tabla)
            else:
                styles = getSampleStyleSheet()
                contenido.append(Paragraph('No hay libros disponibles en este momento.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    if report_type == 'lectores':
        lectores = lectores_activos(20)
        titulo = 'REPORTE DE LECTORES ACTIVOS'
        contenido = []
        if lectores:
            datos_tabla = [[
                lector.codigo_estudiante,
                f"{lector.nombres} {lector.apellidos}",
                lector.carrera or '-',
                lector.email or '-'
            ] for lector in lectores]
            tabla = _crear_tabla(datos_tabla, ['Código', 'Nombre Completo', 'Carrera', 'Email'], [1.2*inch, 2*inch, 1.5*inch, 2*inch])
            contenido.append(tabla)
        else:
            styles = getSampleStyleSheet()
            contenido.append(Paragraph('No hay lectores activos registrados.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    if report_type == 'prestamos_activos':
        prestamos = prestamos_activos(20)
        titulo = 'REPORTE DE PRÉSTAMOS ACTIVOS'
        contenido = []
        if prestamos:
            datos_tabla = []
            for prestamo in prestamos:
                lector = f"{prestamo.lector.nombres} {prestamo.lector.apellidos}" if prestamo.lector else 'Sin lector'
                libro = prestamo.libro.titulo if prestamo.libro else 'Sin libro'
                fecha_esperada = prestamo.fecha_devolucion_esperada.strftime('%Y-%m-%d') if prestamo.fecha_devolucion_esperada else '-'
                datos_tabla.append([lector, libro, fecha_esperada])
            tabla = _crear_tabla(datos_tabla, ['Lector', 'Libro', 'Fecha Esperada Devolución'], [2*inch, 2.5*inch, 1.5*inch])
            contenido.append(tabla)
        else:
            styles = getSampleStyleSheet()
            contenido.append(Paragraph('No hay préstamos activos en este momento.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    if report_type == 'multas':
        multas = multas_pendientes(20)
        titulo = 'REPORTE DE MULTAS PENDIENTES'
        contenido = []
        if multas:
            datos_tabla = []
            for multa in multas:
                lector = f"{multa.lector.nombres} {multa.lector.apellidos}" if multa.lector else 'Sin lector'
                datos_tabla.append([lector, f"S/. {float(multa.monto):.2f}", multa.motivo or '-'])
            tabla = _crear_tabla(datos_tabla, ['Lector', 'Monto', 'Motivo'], [2*inch, 1.2*inch, 2.8*inch])
            contenido.append(tabla)
        else:
            styles = getSampleStyleSheet()
            contenido.append(Paragraph('No hay multas pendientes registradas.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    if report_type == 'devoluciones_pendientes':
        vencidos = prestamos_vencidos(20)
        titulo = 'REPORTE DE PRÉSTAMOS VENCIDOS'
        contenido = []
        if vencidos:
            datos_tabla = []
            for prestamo in vencidos:
                lector = f"{prestamo.lector.nombres} {prestamo.lector.apellidos}" if prestamo.lector else 'Sin lector'
                libro = prestamo.libro.titulo if prestamo.libro else 'Sin libro'
                fecha_vencimiento = prestamo.fecha_devolucion_esperada.strftime('%Y-%m-%d') if prestamo.fecha_devolucion_esperada else '-'
                datos_tabla.append([lector, libro, fecha_vencimiento])
            tabla = _crear_tabla(datos_tabla, ['Lector', 'Libro', 'Vencido Desde'], [2*inch, 2.5*inch, 1.5*inch])
            contenido.append(tabla)
        else:
            styles = getSampleStyleSheet()
            contenido.append(Paragraph('No hay préstamos vencidos en este momento.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    if report_type == 'libros_danios':
        datos = libros_dañados_recientes(30)
        titulo = 'REPORTE DE LIBROS DAÑADOS'
        contenido = []
        if datos:
            datos_tabla = [[titulo_libro, str(total)] for titulo_libro, total in datos]
            tabla = _crear_tabla(datos_tabla, ['Título del Libro', 'Total Daños'], [4*inch, 1.5*inch])
            contenido.append(tabla)
        else:
            styles = getSampleStyleSheet()
            contenido.append(Paragraph('No hay reportes de daños recientes.', styles['Normal']))
        return _crear_pdf_reporte(titulo, contenido), titulo, contenido

    return None, None, None


def generar_reporte(report_type):
    """Genera un PDF detallado y devuelve la ruta del archivo."""
    try:
        if not has_app_context():
            from app import app as flask_app
            with flask_app.app_context():
                pdf_path, titulo, _ = _generar_pdf_por_tipo(report_type)
        else:
            pdf_path, titulo, _ = _generar_pdf_por_tipo(report_type)

        if not pdf_path:
            return {'exito': False, 'mensaje': 'Tipo de reporte no disponible.', 'tipo': report_type}

        mensaje = f"📄 Se adjunta el reporte PDF: {titulo}."
        return {
            'exito': True,
            'mensaje': mensaje,
            'tipo': report_type,
            'pdf_path': pdf_path,
            'titulo': titulo,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Error generando reporte PDF {report_type}: {e}")
        import traceback
        traceback.print_exc()
        return {'exito': False, 'mensaje': 'No fue posible generar el reporte PDF.', 'tipo': report_type}
