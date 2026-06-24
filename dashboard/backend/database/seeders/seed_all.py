"""
Seeders para la base de datos Bibliouni.
Inserta 10 registros de prueba en cada tabla.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from models.base import engine
from models import (
    Autor, Categoria, Libro, Lector, Prestamo,
    Devolucion, Multa, UsuarioSistema, Auditoria
)
from werkzeug.security import generate_password_hash

Session = sessionmaker(bind=engine)


def seed_autores(session):
    if session.query(Autor).count() > 0:
        print("[INFO] Autores ya tienen datos.")
        return
    autores = [
        Autor(nombre='Gabriel', apellido='García Márquez', nacionalidad='Colombiana', fecha_nacimiento=datetime(1927, 3, 6), biografia='Nobel de Literatura 1982'),
        Autor(nombre='Mario', apellido='Vargas Llosa', nacionalidad='Peruana', fecha_nacimiento=datetime(1936, 3, 28), biografia='Nobel de Literatura 2010'),
        Autor(nombre='Julio', apellido='Cortázar', nacionalidad='Argentina', fecha_nacimiento=datetime(1914, 8, 26), biografia='Figura del boom latinoamericano'),
        Autor(nombre='Isabel', apellido='Allende', nacionalidad='Chilena', fecha_nacimiento=datetime(1942, 8, 2), biografia='Autora de La casa de los espíritus'),
        Autor(nombre='Jorge', apellido='Borges', nacionalidad='Argentina', fecha_nacimiento=datetime(1899, 8, 24), biografia='Escritor de ficciones y ensayos'),
        Autor(nombre='Pablo', apellido='Neruda', nacionalidad='Chilena', fecha_nacimiento=datetime(1904, 7, 12), biografia='Poeta y diplomático, Nobel 1971'),
        Autor(nombre='José', apellido='Martí', nacionalidad='Cubana', fecha_nacimiento=datetime(1853, 1, 28), biografia='Héroe nacional de Cuba'),
        Autor(nombre='Ernesto', apellido='Sábato', nacionalidad='Argentina', fecha_nacimiento=datetime(1911, 6, 24), biografia='Escritor y físico'),
        Autor(nombre='Octavio', apellido='Paz', nacionalidad='Mexicana', fecha_nacimiento=datetime(1914, 3, 31), biografia='Poeta y ensayista, Nobel 1990'),
        Autor(nombre='Laura', apellido='Esquivel', nacionalidad='Mexicana', fecha_nacimiento=datetime(1950, 9, 30), biografia='Autora de Como agua para chocolate'),
    ]
    session.add_all(autores)
    session.commit()
    print("[OK] 10 autores insertados.")


def seed_categorias(session):
    if session.query(Categoria).count() > 0:
        print("[INFO] Categorías ya tienen datos.")
        return
    categorias = [
        Categoria(nombre='Literatura', descripcion='Obras literarias de ficción y poesía'),
        Categoria(nombre='Ciencia', descripcion='Libros de ciencias naturales y exactas'),
        Categoria(nombre='Historia', descripcion='Eventos históricos y biografías'),
        Categoria(nombre='Tecnología', descripcion='Informática, ingeniería y tecnología'),
        Categoria(nombre='Filosofía', descripcion='Pensamiento y teoría filosófica'),
        Categoria(nombre='Derecho', descripcion='Legislación, jurisprudencia y derecho'),
        Categoria(nombre='Medicina', descripcion='Ciencias de la salud'),
        Categoria(nombre='Arte', descripcion='Pintura, música, arquitectura y escultura'),
        Categoria(nombre='Economía', descripcion='Teoría económica y finanzas'),
        Categoria(nombre='Psicología', descripcion='Conducta humana y salud mental'),
    ]
    session.add_all(categorias)
    session.commit()
    print("[OK] 10 categorías insertadas.")


def seed_libros(session):
    if session.query(Libro).count() > 0:
        print("[INFO] Libros ya tienen datos.")
        return
    libros = [
        Libro(titulo='Cien años de soledad', isbn='9780307474728', anio_publicacion=1967, editorial='Sudamericana', ejemplares_total=5, ejemplares_disponibles=5, autor_id=1, categoria_id=1),
        Libro(titulo='La ciudad y los perros', isbn='9788466333783', anio_publicacion=1963, editorial='Seix Barral', ejemplares_total=3, ejemplares_disponibles=3, autor_id=2, categoria_id=1),
        Libro(titulo='Rayuela', isbn='9788437634598', anio_publicacion=1963, editorial='Sudamericana', ejemplares_total=4, ejemplares_disponibles=4, autor_id=3, categoria_id=1),
        Libro(titulo='La casa de los espíritus', isbn='9780553383805', anio_publicacion=1982, editorial='Knopf', ejemplares_total=6, ejemplares_disponibles=6, autor_id=4, categoria_id=1),
        Libro(titulo='Ficciones', isbn='9788432215370', anio_publicacion=1944, editorial='Emecé', ejemplares_total=3, ejemplares_disponibles=3, autor_id=5, categoria_id=1),
        Libro(titulo='Veinte poemas de amor', isbn='9788437607066', anio_publicacion=1924, editorial='Nascimento', ejemplares_total=4, ejemplares_disponibles=4, autor_id=6, categoria_id=1),
        Libro(titulo='Isla Negra', isbn='9788432215431', anio_publicacion=1964, editorial='Losada', ejemplares_total=2, ejemplares_disponibles=2, autor_id=6, categoria_id=1),
        Libro(titulo='El túnel', isbn='9788432210146', anio_publicacion=1948, editorial='Sur', ejemplares_total=3, ejemplares_disponibles=3, autor_id=8, categoria_id=1),
        Libro(titulo='El laberinto de la soledad', isbn='9789681603628', anio_publicacion=1950, editorial='Cuadernos Americanos', ejemplares_total=5, ejemplares_disponibles=5, autor_id=9, categoria_id=5),
        Libro(titulo='Como agua para chocolate', isbn='9780385420177', anio_publicacion=1989, editorial='Doubleday', ejemplares_total=7, ejemplares_disponibles=7, autor_id=10, categoria_id=1),
    ]
    session.add_all(libros)
    session.commit()
    print("[OK] 10 libros insertados.")


def seed_lectores(session):
    if session.query(Lector).count() > 0:
        print("[INFO] Lectores ya tienen datos.")
        return
    lectores = [
        Lector(codigo_estudiante='20210001', nombres='Carlos', apellidos='Ramírez López', email='c.ramirez@uni.edu', telefono='987654321', carrera='Ingeniería de Sistemas', facultad='Ingeniería', activo=True),
        Lector(codigo_estudiante='20210002', nombres='Ana', apellidos='Fernández Castro', email='a.fernandez@uni.edu', telefono='987654322', carrera='Derecho', facultad='Derecho y Ciencias Políticas', activo=True),
        Lector(codigo_estudiante='20210003', nombres='Luis', apellidos='Mendoza Silva', email='l.mendoza@uni.edu', telefono='987654323', carrera='Medicina', facultad='Medicina', activo=True),
        Lector(codigo_estudiante='20210004', nombres='María', apellidos='Torres Vega', email='m.torres@uni.edu', telefono='987654324', carrera='Arquitectura', facultad='Ingeniería', activo=True),
        Lector(codigo_estudiante='20210005', nombres='Pedro', apellidos='Gómez Díaz', email='p.gomez@uni.edu', telefono='987654325', carrera='Economía', facultad='Ciencias Económicas', activo=True),
        Lector(codigo_estudiante='20210006', nombres='Lucía', apellidos='Herrera Paredes', email='l.herrera@uni.edu', telefono='987654326', carrera='Psicología', facultad='Ciencias Sociales', activo=True),
        Lector(codigo_estudiante='20210007', nombres='Javier', apellidos='Ruiz Morales', email='j.ruiz@uni.edu', telefono='987654327', carrera='Literatura', facultad='Letras', activo=True),
        Lector(codigo_estudiante='20210008', nombres='Sofía', apellidos='Vargas Núñez', email='s.vargas@uni.edu', telefono='987654328', carrera='Biología', facultad='Ciencias', activo=True),
        Lector(codigo_estudiante='20210009', nombres='Diego', apellidos='Castro Rojas', email='d.castro@uni.edu', telefono='987654329', carrera='Física', facultad='Ciencias', activo=True),
        Lector(codigo_estudiante='20210010', nombres='Elena', apellidos='Navarro Quispe', email='e.navarro@uni.edu', telefono='987654330', carrera='Química', facultad='Ciencias', activo=True),
    ]
    session.add_all(lectores)
    session.commit()
    print("[OK] 10 lectores insertados.")


def seed_prestamos(session):
    if session.query(Prestamo).count() > 0:
        print("[INFO] Préstamos ya tienen datos.")
        return
    hoy = datetime.now()
    prestamos = [
        Prestamo(lector_id=1, libro_id=1, fecha_prestamo=hoy - timedelta(days=5), fecha_devolucion_esperada=hoy + timedelta(days=9), estado='activo'),
        Prestamo(lector_id=2, libro_id=2, fecha_prestamo=hoy - timedelta(days=10), fecha_devolucion_esperada=hoy + timedelta(days=4), estado='activo'),
        Prestamo(lector_id=3, libro_id=3, fecha_prestamo=hoy - timedelta(days=2), fecha_devolucion_esperada=hoy + timedelta(days=12), estado='activo'),
        Prestamo(lector_id=4, libro_id=4, fecha_prestamo=hoy - timedelta(days=15), fecha_devolucion_esperada=hoy - timedelta(days=1), estado='vencido'),
        Prestamo(lector_id=5, libro_id=5, fecha_prestamo=hoy - timedelta(days=20), fecha_devolucion_esperada=hoy - timedelta(days=6), fecha_devolucion_real=hoy - timedelta(days=5), estado='devuelto'),
        Prestamo(lector_id=6, libro_id=6, fecha_prestamo=hoy - timedelta(days=3), fecha_devolucion_esperada=hoy + timedelta(days=11), estado='activo'),
        Prestamo(lector_id=7, libro_id=7, fecha_prestamo=hoy - timedelta(days=8), fecha_devolucion_esperada=hoy + timedelta(days=6), estado='activo'),
        Prestamo(lector_id=8, libro_id=8, fecha_prestamo=hoy - timedelta(days=12), fecha_devolucion_esperada=hoy + timedelta(days=2), estado='activo'),
        Prestamo(lector_id=9, libro_id=9, fecha_prestamo=hoy - timedelta(days=25), fecha_devolucion_esperada=hoy - timedelta(days=11), fecha_devolucion_real=hoy - timedelta(days=10), estado='devuelto'),
        Prestamo(lector_id=10, libro_id=10, fecha_prestamo=hoy - timedelta(days=1), fecha_devolucion_esperada=hoy + timedelta(days=13), estado='activo'),
    ]
    session.add_all(prestamos)
    session.commit()
    print("[OK] 10 préstamos insertados.")


def seed_devoluciones(session):
    if session.query(Devolucion).count() > 0:
        print("[INFO] Devoluciones ya tienen datos.")
        return
    hoy = datetime.now()
    devoluciones = [
        Devolucion(prestamo_id=5, fecha_devolucion=hoy - timedelta(days=5), estado_libro='bueno', observaciones='Devuelto en buen estado'),
        Devolucion(prestamo_id=9, fecha_devolucion=hoy - timedelta(days=10), estado_libro='dañado', observaciones='Portada con pequeña rotura'),
        Devolucion(prestamo_id=1, fecha_devolucion=hoy, estado_libro='bueno', observaciones='Devuelto correctamente'),
        Devolucion(prestamo_id=2, fecha_devolucion=hoy, estado_libro='bueno', observaciones='Sin novedades'),
        Devolucion(prestamo_id=3, fecha_devolucion=hoy, estado_libro='bueno', observaciones='En perfecto estado'),
        Devolucion(prestamo_id=4, fecha_devolucion=hoy, estado_libro='perdido', observaciones='El lector reportó pérdida'),
        Devolucion(prestamo_id=6, fecha_devolucion=hoy, estado_libro='bueno', observaciones='Todo bien'),
        Devolucion(prestamo_id=7, fecha_devolucion=hoy, estado_libro='bueno', observaciones='Sin problemas'),
        Devolucion(prestamo_id=8, fecha_devolucion=hoy, estado_libro='dañado', observaciones='Páginas dobladas'),
        Devolucion(prestamo_id=10, fecha_devolucion=hoy, estado_libro='bueno', observaciones='Devolución temprana'),
    ]
    session.add_all(devoluciones)
    session.commit()
    print("[OK] 10 devoluciones insertadas.")


def seed_multas(session):
    if session.query(Multa).count() > 0:
        print("[INFO] Multas ya tienen datos.")
        return
    multas = [
        Multa(lector_id=4, prestamo_id=4, monto=15.00, motivo='Retraso de 1 día', pagada=False),
        Multa(lector_id=9, prestamo_id=9, monto=5.00, motivo='Daño leve en portada', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=8, prestamo_id=8, monto=10.00, motivo='Páginas dobladas', pagada=False),
        Multa(lector_id=1, prestamo_id=1, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=2, prestamo_id=2, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=3, prestamo_id=3, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=5, prestamo_id=5, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=6, prestamo_id=6, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=7, prestamo_id=7, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
        Multa(lector_id=10, prestamo_id=10, monto=0.00, motivo='Sin multa', pagada=True, fecha_pago=datetime.now()),
    ]
    session.add_all(multas)
    session.commit()
    print("[OK] 10 multas insertadas.")


def seed_usuarios_sistema(session):
    if session.query(UsuarioSistema).count() > 0:
        print("[INFO] Usuarios del sistema ya tienen datos.")
        return
    usuarios = [
        UsuarioSistema(username='admin', password_hash=generate_password_hash('admin123'), nombre_completo='Administrador General', rol='admin', activo=True, ultimo_acceso=datetime.now()),
        UsuarioSistema(username='biblio1', password_hash=generate_password_hash('biblio123'), nombre_completo='Juan Pérez', rol='bibliotecario', activo=True, ultimo_acceso=datetime.now()),
        UsuarioSistema(username='biblio2', password_hash=generate_password_hash('biblio123'), nombre_completo='María López', rol='bibliotecario', activo=True, ultimo_acceso=datetime.now()),
        UsuarioSistema(username='biblio3', password_hash=generate_password_hash('biblio123'), nombre_completo='Carlos Ruiz', rol='bibliotecario', activo=True, ultimo_acceso=datetime.now()),
        UsuarioSistema(username='biblio4', password_hash=generate_password_hash('biblio123'), nombre_completo='Ana Castro', rol='bibliotecario', activo=True),
        UsuarioSistema(username='biblio5', password_hash=generate_password_hash('biblio123'), nombre_completo='Luis Torres', rol='bibliotecario', activo=True),
        UsuarioSistema(username='biblio6', password_hash=generate_password_hash('biblio123'), nombre_completo='Sofía Vega', rol='bibliotecario', activo=False),
        UsuarioSistema(username='biblio7', password_hash=generate_password_hash('biblio123'), nombre_completo='Diego Morales', rol='bibliotecario', activo=True),
        UsuarioSistema(username='biblio8', password_hash=generate_password_hash('biblio123'), nombre_completo='Elena Rojas', rol='bibliotecario', activo=True),
        UsuarioSistema(username='biblio9', password_hash=generate_password_hash('biblio123'), nombre_completo='Pedro Quispe', rol='bibliotecario', activo=True),
    ]
    session.add_all(usuarios)
    session.commit()
    print("[OK] 10 usuarios del sistema insertados.")


def seed_auditoria(session):
    if session.query(Auditoria).count() > 0:
        print("[INFO] Auditoría ya tiene datos.")
        return
    registros = [
        Auditoria(tipo_operacion='LOGIN', modulo='Sistema', descripcion='Inicio de sesión exitoso', usuario='admin', resultado='Éxito', detalle='IP: 127.0.0.1'),
        Auditoria(tipo_operacion='CREATE', modulo='Libros', descripcion='Registro de nuevo libro', usuario='biblio1', resultado='Éxito', detalle='Libro ID 1 registrado'),
        Auditoria(tipo_operacion='UPDATE', modulo='Prestamos', descripcion='Actualización de préstamo', usuario='biblio2', resultado='Éxito', detalle='Préstamo ID 1 actualizado'),
        Auditoria(tipo_operacion='DELETE', modulo='Lectores', descripcion='Eliminación de lector', usuario='admin', resultado='Éxito', detalle='Lector ID 5 eliminado'),
        Auditoria(tipo_operacion='CREATE', modulo='Multas', descripcion='Generación de multa', usuario='biblio1', resultado='Éxito', detalle='Multa ID 1 generada'),
        Auditoria(tipo_operacion='LOGIN', modulo='Sistema', descripcion='Intento de login fallido', usuario='desconocido', resultado='Fallo', detalle='Contraseña incorrecta'),
        Auditoria(tipo_operacion='REPORT', modulo='Reportes', descripcion='Generación de reporte mensual', usuario='admin', resultado='Éxito', detalle='Reporte de préstamos descargado'),
        Auditoria(tipo_operacion='UPDATE', modulo='Usuarios', descripcion='Cambio de rol de usuario', usuario='admin', resultado='Éxito', detalle='Usuario biblio3 cambiado a admin'),
        Auditoria(tipo_operacion='CREATE', modulo='Devoluciones', descripcion='Registro de devolución', usuario='biblio2', resultado='Éxito', detalle='Devolución ID 2 registrada'),
        Auditoria(tipo_operacion='BACKUP', modulo='Monitoreo', descripcion='Respaldo de base de datos', usuario='sistema', resultado='Éxito', detalle='Backup completado a las 02:00 AM'),
    ]
    session.add_all(registros)
    session.commit()
    print("[OK] 10 registros de auditoría insertados.")


if __name__ == '__main__':
    print("=" * 60)
    print("  SEEDERS - BIBLIOUNI")
    print("=" * 60)
    session = Session()
    try:
        seed_autores(session)
        seed_categorias(session)
        seed_libros(session)
        seed_lectores(session)
        seed_prestamos(session)
        seed_devoluciones(session)
        seed_multas(session)
        seed_usuarios_sistema(session)
        seed_auditoria(session)
        print("=" * 60)
        print("[OK] Todos los seeders ejecutados correctamente.")
    except Exception as e:
        print(f"[ERROR] {e}")
        session.rollback()
    finally:
        session.close()
