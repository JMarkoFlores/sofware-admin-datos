"""
Inicialización de la base de datos Bibliouni.
Crea la base de datos (si no existe) y todas las tablas usando SQLAlchemy.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pyodbc
from sqlalchemy import inspect
from config.settings import Config
from models.base import engine, Base


def create_database_if_not_exists():
    """Crea la base de datos Bibliouni si no existe."""
    server = Config.BIBLIOUNI_SERVER
    driver = Config.BIBLIOUNI_DRIVER
    db_name = Config.BIBLIOUNI_DB

    conn_str = f"DRIVER={{{driver}}};SERVER={server};Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{db_name}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"[OK] Base de datos '{db_name}' creada.")
    else:
        print(f"[INFO] Base de datos '{db_name}' ya existe.")

    cursor.close()
    conn.close()


def create_tables():
    """Crea todas las tablas definidas en los modelos SQLAlchemy."""
    from models import Autor, Categoria, Libro, Lector, Prestamo, Devolucion, Multa, UsuarioSistema, Auditoria, UserConversation
    Base.metadata.create_all(engine)
    print("[OK] Tablas creadas exitosamente.")


if __name__ == '__main__':
    print("=" * 60)
    print("  INICIALIZACIÓN DE BASE DE DATOS - BIBLIOUNI")
    print("=" * 60)
    create_database_if_not_exists()
    create_tables()
    print("=" * 60)
