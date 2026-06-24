"""
Configuraciones centralizadas del proyecto.
Lee variables desde el archivo .env
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # SQL Server - Bibliouni (ORM)
    BIBLIOUNI_SERVER = os.getenv('BIBLIOUNI_SERVER', 'Jeanmarko')
    BIBLIOUNI_DB = os.getenv('BIBLIOUNI_DB', 'Bibliouni')
    BIBLIOUNI_USER = os.getenv('BIBLIOUNI_USER', '')
    BIBLIOUNI_PASSWORD = os.getenv('BIBLIOUNI_PASSWORD', '')
    BIBLIOUNI_DRIVER = os.getenv('BIBLIOUNI_DRIVER', 'ODBC Driver 17 for SQL Server')
    BIBLIOUNI_TRUSTED = os.getenv('BIBLIOUNI_TRUSTED_CONNECTION', 'yes').lower()

    # SQL Server - TenebrosaOLTP (Disparador - pyodbc directo)
    DB_SERVER = os.getenv('DB_SERVER', 'Jeanmarko')
    DB_NAME = os.getenv('DB_NAME', 'TenebrosaOLTP')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    DB_TRUSTED = os.getenv('DB_TRUSTED_CONNECTION', 'yes').lower()

    # Evolution API
    EVOLUTION_URL = os.getenv('EVOLUTION_URL', 'http://localhost:8080')
    EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', 'mi-api-key-secreta-123')
    EVOLUTION_INSTANCE = os.getenv('EVOLUTION_INSTANCE', 'jean')
    WHATSAPP_DESTINATION = os.getenv('WHATSAPP_DESTINATION', '51952310138')

    @classmethod
    def get_bibliouni_connection_string(cls):
        if cls.BIBLIOUNI_TRUSTED == 'yes':
            return (
                f"DRIVER={{{cls.BIBLIOUNI_DRIVER}}};"
                f"SERVER={cls.BIBLIOUNI_SERVER};"
                f"DATABASE={cls.BIBLIOUNI_DB};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{cls.BIBLIOUNI_DRIVER}}};"
                f"SERVER={cls.BIBLIOUNI_SERVER};"
                f"DATABASE={cls.BIBLIOUNI_DB};"
                f"UID={cls.BIBLIOUNI_USER};"
                f"PWD={cls.BIBLIOUNI_PASSWORD};"
            )

    @classmethod
    def get_tenebrosa_connection_string(cls):
        if cls.DB_TRUSTED == 'yes':
            return (
                f"DRIVER={{{cls.DB_DRIVER}}};"
                f"SERVER={cls.DB_SERVER};"
                f"DATABASE={cls.DB_NAME};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{cls.DB_DRIVER}}};"
                f"SERVER={cls.DB_SERVER};"
                f"DATABASE={cls.DB_NAME};"
                f"UID={cls.DB_USER};"
                f"PWD={cls.DB_PASSWORD};"
            )
