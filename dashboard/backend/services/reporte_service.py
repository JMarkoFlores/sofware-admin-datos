"""
Servicio para generación de reportes detallados en PDF para WhatsApp.
============================================================

La lógica de consultas se ejecuta en SQL Server mediante Stored Procedures.
Este servicio solo formatea los datos y genera el PDF.
"""

import os
import re
import pyodbc
from datetime import datetime, timedelta
from pathlib import Path

from flask import has_app_context
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.settings import Config

REPORTS_OUTPUT_DIR = os.getenv(
    'REPORTS_OUTPUT_DIR',
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
)


def _get_bibliouni_connection_string():
    """Cadena de conexión pyodbc a Bibliouni."""
    if Config.BIBLIOUNI_TRUSTED == 'yes':
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=Bibliouni;"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=Bibliouni;"
            f"UID={Config.BIBLIOUNI_USER};"
            f"PWD={Config.BIBLIOUNI_PASSWORD};"
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


def estadisticas_generales():
    """Estadísticas generales de la biblioteca - llama a SP."""
    conn_str = _get_bibliouni_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Bibliouni.dbo.sp_reporte_estadisticas_generales")
            row = cursor.fetchone()
            if row:
                return {
                    'total_libros': row.total_libros or 0,
                    'libros_disponibles': row.libros_disponibles or 0,
                    'total_autores': row.total_autores or 0,
                    'total_categorias': row.total_categorias or 0,
                    'total_lectores': row.total_lectores or 0,
                    'prestamos_activos': row.prestamos_activos or 0,
                    'multas_pendientes': row.multas_pendientes or 0,
                    'monto_multas_pendientes': float(row.monto_multas_pendientes or 0)
                }
            return {
                'total_libros': 0, 'libros_disponibles': 0, 'total_autores': 0,
                'total_categorias': 0, 'total_lectores': 0, 'prestamos_activos': 0,
                'multas_pendientes': 0, 'monto_multas_pendientes': 0.0
            }
    except Exception as e:
        print(f"[ERROR] Error ejecutando sp_reporte_estadisticas_generales: {e}")
        return {
            'total_libros': 0, 'libros_disponibles': 0, 'total_autores': 0,
            'total_categorias': 0, 'total_lectores': 0, 'prestamos_activos': 0,
            'multas_pendientes': 0, 'monto_multas_pendientes': 0.0
        }


def libros_mas_prestados(limit=20):
    """Libros más prestados - llama a SP."""
    conn_str = _get_bibliouni_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Bibliouni.dbo.sp_reporte_libros_mas_prestados @top_n = ?", (limit,))
            rows = cursor.fetchall()
            return [(row.titulo_libro, row.total_prestamos) for row in rows]
    except Exception as e:
        print(f"[ERROR] Error ejecutando sp_reporte_libros_mas_prestados: {e}")
        return []


def multas_pendientes(limit=20):
    """Multas pendientes - llama a SP."""
    conn_str = _get_bibliouni_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Bibliouni.dbo.sp_reporte_multas_pendientes @top_n = ?", (limit,))
            rows = cursor.fetchall()
            return [(row.lector, float(row.monto), row.motivo) for row in rows]
    except Exception as e:
        print(f"[ERROR] Error ejecutando sp_reporte_multas_pendientes: {e}")
        return []


def prestamos_vencidos(limit=20):
    """Préstamos vencidos - llama a SP."""
    conn_str = _get_bibliouni_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Bibliouni.dbo.sp_reporte_prestamos_vencidos @top_n = ?", (limit,))
            rows = cursor.fetchall()
            return [(row.lector, row.libro, row.vencido_desde) for row in rows]
    except Exception as e:
        print(f"[ERROR] Error ejecutando sp_reporte_prestamos_vencidos: {e}")
        return []


def libros_dañados_recientes(dias=30):
    """Libros dañados recientes - llama a SP."""
    conn_str = _get_bibliouni_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Bibliouni.dbo.sp_reporte_libros_danhados @dias = ?", (dias,))
            rows = cursor.fetchall()
            return [(row.titulo_libro, row.total_danios) for row in rows]
    except Exception as e:
        print(f"[ERROR] Error ejecutando sp_reporte_libros_danhados: {e}")
        return []


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
            datos_tabla = [[titulo_libro, str(total)] for titulo_libro, total in libros]
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
            datos_tabla = [[lector, f"S/. {monto:.2f}", motivo or '-'] for lector, monto, motivo in multas]
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
            datos_tabla = [[lector, libro, fecha_vencimiento] for lector, libro, fecha_vencimiento in vencidos]
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
