"""
SQLAlchemy Base y configuración de conexión para la base de datos Bibliouni.
"""

from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from config.settings import Config

# Engine para SQL Server con pyodbc
odbc_str = Config.get_bibliouni_connection_string()
connection_url = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)

engine = create_engine(connection_url, pool_pre_ping=True)

Base = declarative_base()

db = SQLAlchemy(model_class=Base)
