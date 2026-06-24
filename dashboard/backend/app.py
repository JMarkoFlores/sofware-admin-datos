"""
Backend Flask - Sistema de Biblioteca Universitaria
====================================================

API REST para la gestión operativa de la biblioteca y monitoreo
de base de datos con notificaciones por WhatsApp.

Módulos bibliotecarios: conectados a Bibliouni vía SQLAlchemy ORM.
Módulo Disparador: conectado a TenebrosaOLTP vía pyodbc (INTACTO).
"""

import os
from urllib.parse import quote_plus
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from config.settings import Config
from models.base import db

# Importar blueprints de módulos bibliotecarios
from routes import (
    autores, categorias, libros, lectores, prestamos,
    devoluciones, multas, usuarios_sistema, reportes,
    auditoria, dashboard, disparador
)

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar SQLAlchemy para Bibliouni
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc:///?odbc_connect="
    + quote_plus(Config.get_bibliouni_connection_string())
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db.init_app(app)

# Registrar blueprints
app.register_blueprint(autores.bp)
app.register_blueprint(categorias.bp)
app.register_blueprint(libros.bp)
app.register_blueprint(lectores.bp)
app.register_blueprint(prestamos.bp)
app.register_blueprint(devoluciones.bp)
app.register_blueprint(multas.bp)
app.register_blueprint(usuarios_sistema.bp)
app.register_blueprint(reportes.bp)
app.register_blueprint(auditoria.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(disparador.bp)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Sistema de Biblioteca Universitaria activo',
        'modulos': [
            'libros', 'autores', 'categorias', 'lectores',
            'prestamos', 'devoluciones', 'multas', 'usuarios',
            'reportes', 'auditoria', 'dashboard', 'disparador'
        ]
    })


if __name__ == '__main__':
    port = Config.FLASK_PORT
    debug = Config.FLASK_DEBUG

    print("=" * 60)
    print("  SISTEMA DE BIBLIOTECA UNIVERSITARIA - BACKEND")
    print("=" * 60)
    print(f"  API: http://localhost:{port}")
    print(f"  Bibliouni: {Config.BIBLIOUNI_SERVER}/{Config.BIBLIOUNI_DB}")
    print(f"  TenebrosaOLTP: {Config.DB_SERVER}/{Config.DB_NAME}")
    print(f"  Evolution API: {Config.EVOLUTION_URL}")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=debug)
