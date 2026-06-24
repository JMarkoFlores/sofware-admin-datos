"""
Repositorio para consultas complejas en la base de datos Bibliouni.
"""

from sqlalchemy import text
from models.base import engine


def ejecutar_query_raw(sql, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]
