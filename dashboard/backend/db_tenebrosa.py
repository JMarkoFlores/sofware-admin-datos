"""
Módulo de conexión a SQL Server
==============================

Obtiene la cantidad de tablas y sus nombres de la base de datos TenebrosaOLTP.
"""

import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv('DB_SERVER', 'Jeanmarko')
DB_NAME = os.getenv('DB_NAME', 'TenebrosaOLTP')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
DB_TRUSTED = os.getenv('DB_TRUSTED_CONNECTION', 'yes').lower()


def get_connection_string():
    """Construye la cadena de conexión a SQL Server."""
    if DB_TRUSTED == 'yes':
        return (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
        )


def get_tables_info():
    """
    Obtiene la cantidad de tablas y sus nombres.
    
    Returns:
        dict: { 'count': int, 'names': list }
    """
    conn_str = get_connection_string()
    
    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Obtener nombres de tablas de usuario
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                AND TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            return {
                'count': len(tables),
                'names': tables
            }
            
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return {
            'count': 0,
            'names': [],
            'error': str(e)
        }


if __name__ == '__main__':
    # Prueba
    info = get_tables_info()
    print(f"Tablas encontradas: {info['count']}")
    print(f"Nombres: {info['names']}")
