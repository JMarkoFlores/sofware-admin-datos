"""
Servicio de monitoreo y ejecución de backups para Bibliouni.
============================================================

- Verifica si existe un backup del día actual en msdb.dbo.backupset.
- Ejecuta backup manual vía T-SQL BACKUP DATABASE.
- Envía alertas y confirmaciones por WhatsApp.
- Registra eventos en auditoría.
"""

import os
import socket
import pyodbc
from datetime import datetime
from config.settings import Config
from utils.helpers import log_auditoria
from whatsapp import send_message

# Ruta por defecto: carpeta accesible para SQL Server
DEFAULT_BACKUP_PATH = r'C:\Temp\BibliouniBackups'
BACKUP_PATH = os.getenv('BACKUP_PATH', DEFAULT_BACKUP_PATH)


def _get_bibliouni_connection_string():
    """Cadena de conexión pyodbc a Bibliouni (master para ejecutar BACKUP)."""
    if Config.BIBLIOUNI_TRUSTED == 'yes':
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=master;"
            f"UID={Config.BIBLIOUNI_USER};"
            f"PWD={Config.BIBLIOUNI_PASSWORD};"
        )


def _get_bibliouni_connection_string_msdb():
    """Cadena de conexión pyodbc a msdb para consultar backupset."""
    if Config.BIBLIOUNI_TRUSTED == 'yes':
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=msdb;"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=msdb;"
            f"UID={Config.BIBLIOUNI_USER};"
            f"PWD={Config.BIBLIOUNI_PASSWORD};"
        )


def verificar_backup_hoy():
    """
    Verifica si existe un backup de Bibliouni realizado hoy Y que el archivo
    físico aún exista en disco (evita falsos positivos si borraron el .bak).

    Returns:
        dict: {'existe': bool, 'detalle': str}
    """
    conn_str = _get_bibliouni_connection_string_msdb()
    hoy = datetime.now().strftime('%Y-%m-%d')

    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            # Obtener la ruta física del backup más reciente de hoy
            cursor.execute("""
                SELECT TOP 1 mf.physical_device_name
                FROM msdb.dbo.backupset bs
                JOIN msdb.dbo.backupmediafamily mf ON bs.media_set_id = mf.media_set_id
                WHERE bs.database_name = ?
                  AND bs.backup_start_date >= CAST(GETDATE() AS DATE)
                ORDER BY bs.backup_start_date DESC
            """, (Config.BIBLIOUNI_DB,))
            row = cursor.fetchone()

            if not row:
                return {
                    'existe': False,
                    'detalle': f'No se encontró registro de backup de {Config.BIBLIOUNI_DB} para el {hoy}.'
                }

            ruta_backup = row[0]
            print(f"[DEBUG Backup] Último backup registrado: {ruta_backup}")

            # Verificar que el archivo físico exista y tenga contenido
            if os.path.exists(ruta_backup) and os.path.getsize(ruta_backup) > 0:
                tamano_mb = os.path.getsize(ruta_backup) / (1024 * 1024)
                return {
                    'existe': True,
                    'detalle': f'Backup verificado: {ruta_backup} ({tamano_mb:.2f} MB).'
                }
            else:
                return {
                    'existe': False,
                    'detalle': f'El registro de backup existe pero el archivo fue eliminado o está vacío: {ruta_backup}'
                }

    except Exception as e:
        return {
            'existe': False,
            'detalle': f'Error al verificar backup: {str(e)}'
        }


def _get_bibliouni_db_connection_string():
    """Cadena de conexión pyodbc directamente a la base de datos Bibliouni."""
    if Config.BIBLIOUNI_TRUSTED == 'yes':
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE={Config.BIBLIOUNI_DB};"
            f"Trusted_Connection=yes;"
        )
    else:
        return (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE={Config.BIBLIOUNI_DB};"
            f"UID={Config.BIBLIOUNI_USER};"
            f"PWD={Config.BIBLIOUNI_PASSWORD};"
        )


def obtener_tablas_bibliouni():
    """Obtiene la lista de tablas de usuario en Bibliouni (schema dbo)."""
    conn_str = _get_bibliouni_db_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                  AND TABLE_SCHEMA = 'dbo'
                ORDER BY TABLE_NAME
            """)
            tablas = [row[0] for row in cursor.fetchall()]
            print(f"[DEBUG Backup] Tablas encontradas en {Config.BIBLIOUNI_DB}: {tablas}")
            return tablas
    except Exception as e:
        print(f"[ERROR] No se pudieron obtener tablas: {e}")
        return []


def ejecutar_backup():
    """
    Ejecuta BACKUP DATABASE de Bibliouni a disco.

    Returns:
        dict: {'exito': bool, 'ruta': str, 'mensaje': str}
    """
    print(f"[DEBUG Backup] Iniciando ejecución de backup...")
    print(f"[DEBUG Backup] BACKUP_PATH={BACKUP_PATH}")

    os.makedirs(BACKUP_PATH, exist_ok=True)
    print(f"[DEBUG Backup] Carpeta backup creada/verificada.")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"Bibliouni_{timestamp}.bak"
    ruta_completa = os.path.join(BACKUP_PATH, nombre_archivo)

    # Escapar para SQL Server (doblar backslashes en T-SQL)
    ruta_sql = ruta_completa.replace('\\', '\\\\')

    sql = f"""
    BACKUP DATABASE [{Config.BIBLIOUNI_DB}] 
    TO DISK = N'{ruta_sql}' 
    WITH FORMAT, COMPRESSION, STATS=10;
    """
    print(f"[DEBUG Backup] Archivo destino: {ruta_completa}")
    print(f"[DEBUG Backup] SQL: {sql.strip()}")

    conn_str = _get_bibliouni_connection_string()
    print(f"[DEBUG Backup] Conectando a SQL Server (master)...")

    try:
        with pyodbc.connect(conn_str, timeout=120, autocommit=True) as conn:
            print(f"[DEBUG Backup] Conexión establecida (autocommit=True).")
            cursor = conn.cursor()
            print(f"[DEBUG Backup] Ejecutando BACKUP DATABASE...")
            cursor.execute(sql)
            # Consumir resultados para evitar errores de cursor
            while cursor.nextset():
                pass
            print(f"[DEBUG Backup] Comando ejecutado. Cerrando conexión...")

        # Verificar que el archivo fue creado y tiene tamaño > 0
        print(f"[DEBUG Backup] Verificando archivo...")
        if os.path.exists(ruta_completa) and os.path.getsize(ruta_completa) > 0:
            tamano = os.path.getsize(ruta_completa)
            print(f"[DEBUG Backup] Archivo creado correctamente: {tamano} bytes")
            return {
                'exito': True,
                'ruta': ruta_completa,
                'mensaje': f'Backup generado exitosamente: {nombre_archivo}'
            }
        else:
            print(f"[DEBUG Backup] ERROR: El archivo no existe o está vacío.")
            return {
                'exito': False,
                'ruta': ruta_completa,
                'mensaje': 'El backup pareció ejecutarse pero el archivo no fue encontrado o está vacío.'
            }

    except Exception as e:
        print(f"[DEBUG Backup] ERROR en ejecución: {type(e).__name__}: {str(e)}")
        return {
            'exito': False,
            'ruta': ruta_completa,
            'mensaje': f'Error al ejecutar backup: {str(e)}'
        }


def enviar_alerta_backup_pendiente(numero_destino):
    """Envía alerta por WhatsApp cuando no existe backup del día."""
    mensaje = (
        "🚨 ALERTA DE RESPALDO\n\n"
        "Sistema: Bibliouni\n\n"
        "No se detectó un backup realizado el día de hoy.\n\n"
        "Estado:\n"
        "❌ Backup pendiente\n\n"
        "Para resolver automáticamente responda:\n\n"
        "RESUELVE BACKUP"
    )
    return send_message(mensaje, numero_destino)


def enviar_confirmacion_backup(numero_destino, tablas, ruta_archivo=None):
    """Envía confirmación de backup exitoso con lista de tablas y ruta del archivo."""
    tablas_texto = "\n".join([f"- {t}" for t in tablas]) if tablas else "- (No se pudieron obtener las tablas)"
    ruta_texto = f"\n📁 Archivo:\n{ruta_archivo}\n" if ruta_archivo else ""
    mensaje = (
        "✅ BACKUP REALIZADO\n\n"
        "Base de datos: Bibliouni\n\n"
        "Estado:\n"
        "Backup generado correctamente.\n"
        f"{ruta_texto}\n"
        "Tablas incluidas:\n"
        f"{tablas_texto}"
    )
    return send_message(mensaje, numero_destino)


def enviar_error_backup(numero_destino):
    """Envía notificación de error al generar backup."""
    mensaje = (
        "❌ ERROR DE BACKUP\n\n"
        "No fue posible generar el respaldo.\n\n"
        "Revise los logs del sistema para más detalles."
    )
    return send_message(mensaje, numero_destino)


def procesar_comando_backup(texto, numero_remoto, numero_destino_configurado):
    """
    Procesa el comando RESUELVE BACKUP recibido por WhatsApp.

    Args:
        texto (str): Texto del mensaje entrante.
        numero_remoto (str): Número del remitente (limpio, sin @s.whatsapp.net).
        numero_destino_configurado (str): Número configurado en el sistema.

    Returns:
        dict: Resultado del procesamiento.
    """
    print(f"[DEBUG procesar_comando_backup] Iniciando...")
    print(f"[DEBUG procesar_comando_backup] texto='{texto}', remoto='{numero_remoto}', destino='{numero_destino_configurado}'")

    texto_limpio = texto.strip().upper()

    # Validar que el comando sea exacto
    if texto_limpio != "RESUELVE BACKUP":
        print(f"[DEBUG procesar_comando_backup] Comando no reconocido: '{texto_limpio}'")
        return {'processed': False, 'reason': 'Comando no reconocido'}

    # Validar que el remitente sea el número destino configurado
    if numero_remoto != numero_destino_configurado:
        print(f"[DEBUG procesar_comando_backup] Número no autorizado: {numero_remoto} != {numero_destino_configurado}")
        return {'processed': False, 'reason': 'Número no autorizado'}

    print(f"[DEBUG procesar_comando_backup] Comando y número validados correctamente.")

    # Registrar intento
    try:
        log_auditoria(
            'BACKUP',
            'Backup',
            'Comando RESUELVE BACKUP recibido. Iniciando backup manual...',
            usuario='sistema',
            resultado='En progreso',
            detalle=f'Origen: {numero_remoto}'
        )
        print(f"[DEBUG procesar_comando_backup] Auditoría (inicio) registrada.")
    except Exception as e:
        print(f"[DEBUG procesar_comando_backup] ERROR al registrar auditoría (inicio): {e}")

    # Ejecutar backup
    print(f"[DEBUG procesar_comando_backup] Llamando a ejecutar_backup()...")
    resultado = ejecutar_backup()
    print(f"[DEBUG procesar_comando_backup] Resultado de ejecutar_backup: exito={resultado['exito']}, mensaje={resultado['mensaje']}")

    if resultado['exito']:
        print(f"[DEBUG procesar_comando_backup] Backup exitoso. Obteniendo tablas...")
        tablas = obtener_tablas_bibliouni()
        print(f"[DEBUG procesar_comando_backup] Tablas obtenidas: {len(tablas)} tablas")
        enviar_confirmacion_backup(numero_destino_configurado, tablas, ruta_archivo=resultado.get('ruta'))
        try:
            log_auditoria(
                'BACKUP',
                'Backup',
                resultado['mensaje'],
                usuario='sistema',
                resultado='Éxito',
                detalle=f'Archivo: {resultado["ruta"]}'
            )
            print(f"[DEBUG procesar_comando_backup] Auditoría (éxito) registrada.")
        except Exception as e:
            print(f"[DEBUG procesar_comando_backup] ERROR al registrar auditoría (éxito): {e}")
        return {'processed': True, 'exito': True, 'mensaje': resultado['mensaje']}
    else:
        print(f"[DEBUG procesar_comando_backup] Backup falló. Enviando mensaje de error...")
        enviar_error_backup(numero_destino_configurado)
        try:
            log_auditoria(
                'ERROR',
                'Backup',
                resultado['mensaje'],
                usuario='sistema',
                resultado='Fallo',
                detalle=f'Origen: {numero_remoto}'
            )
            print(f"[DEBUG procesar_comando_backup] Auditoría (fallo) registrada.")
        except Exception as e:
            print(f"[DEBUG procesar_comando_backup] ERROR al registrar auditoría (fallo): {e}")
        return {'processed': True, 'exito': False, 'mensaje': resultado['mensaje']}
