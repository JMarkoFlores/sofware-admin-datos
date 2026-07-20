"""
Servicio de monitoreo y ejecución de backups para Bibliouni.
============================================================

- Verifica si existe un backup del día actual en msdb.dbo.backupset.
- Ejecuta backup manual vía T-SQL BACKUP DATABASE.
- Envía alertas y confirmaciones por WhatsApp.
- Registra eventos en auditoría.
"""

import os
import re
import socket
import unicodedata
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

#EJECUCIÓN DEL SCRIPT DE LA BD
def verificar_backup_hoy():
    """
    Verifica si existe un backup de Bibliouni realizado hoy llamando al
    Stored Procedure sp_VerificarBackupHoy en msdb.

    Returns:
        dict: {
            'existe': bool,
            'detalle': str,
            'ruta': str or None,
            'hora': str or None,
            'tamano_mb': float or None
        }
    """
    conn_str = _get_bibliouni_connection_string_msdb()
    hoy = datetime.now().strftime('%Y-%m-%d')

    try:
        with pyodbc.connect(conn_str, timeout=15) as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC msdb.dbo.sp_VerificarBackupHoy ?", (Config.BIBLIOUNI_DB,))

            row = cursor.fetchone()
            existe = bool(row[0]) if row[0] is not None else False
            ruta = row[1]
            hora_raw = row[2]
            tamano_mb = row[3]
            mensaje = row[4]

            hora_formateada = None
            if hora_raw is not None:
                hora_formateada = hora_raw.strftime('%H:%M:%S') if hasattr(hora_raw, 'strftime') else str(hora_raw)

            print(f"[DEBUG Backup] SP verificacion: existe={existe}, ruta={ruta}, hora={hora_formateada}")

            return {
                'existe': existe,
                'detalle': mensaje or 'Sin mensaje del SP',
                'ruta': ruta,
                'hora': hora_formateada,
                'tamano_mb': tamano_mb
            }

    except Exception as e:
        return {
            'existe': False,
            'detalle': f'Error al verificar backup: {str(e)}',
            'ruta': None,
            'hora': None,
            'tamano_mb': None
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


#LLAMADA AL SCRIPT DE LA BD
def ejecutar_backup():
    """
    Ejecuta el backup de Bibliouni llamando al Stored Procedure
    sp_EjecutarBackupBibliouni en master.

    Returns:
        dict: {'exito': bool, 'ruta': str, 'mensaje': str}
    """
    print(f"[DEBUG Backup] Iniciando ejecución de backup via SP...")

    conn_str = _get_bibliouni_connection_string()
    print(f"[DEBUG Backup] Conectando a SQL Server (master) para ejecutar SP...")

    try:
        with pyodbc.connect(conn_str, timeout=120, autocommit=True) as conn:
            print(f"[DEBUG Backup] Conexión establecida (autocommit=True).")
            cursor = conn.cursor()
            print(f"[DEBUG Backup] Ejecutando sp_EjecutarBackupBibliouni...")

            cursor.execute("EXEC master.dbo.sp_EjecutarBackupBibliouni ?", (Config.BIBLIOUNI_DB,))

            # El SP ejecuta BACKUP DATABASE con STATS=10, lo que genera multiples
            # mensajes de progreso como result sets intermedios. Consumimos todos
            # hasta llegar al SELECT final que devuelve el resultado.
            row = None
            while True:
                try:
                    if cursor.description:
                        row = cursor.fetchone()
                    if not cursor.nextset():
                        break
                except pyodbc.ProgrammingError:
                    break

            if row:
                exito = bool(row[0]) if row[0] is not None else False
                ruta = row[1]
                mensaje = row[2]
            else:
                # Si no pudimos leer el SELECT final pero el SP no lanzo error,
                # verificamos manualmente si el backup del dia existe.
                print("[DEBUG Backup] No se obtuvo result set del SP. Verificando manualmente...")
                resultado = verificar_backup_hoy()
                exito = resultado.get('existe', False)
                ruta = resultado.get('ruta')
                mensaje = resultado.get('detalle', 'Backup ejecutado. Verificacion manual necesaria.')

            print(f"[DEBUG Backup] SP respuesta: exito={exito}, ruta={ruta}, mensaje={mensaje}")

            return {
                'exito': exito,
                'ruta': ruta,
                'mensaje': mensaje or 'El SP no devolvió mensaje'
            }

    except Exception as e:
        print(f"[DEBUG Backup] ERROR en ejecución: {type(e).__name__}: {str(e)}")
        return {
            'exito': False,
            'ruta': None,
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


def enviar_confirmacion_backup_existente(numero_destino, hora, ruta, tamano_mb=None):
    """
    Envía confirmación cuando ya existe un backup del día actual
    al momento de iniciar el monitoreo.
    """
    tamano_texto = f" ({tamano_mb:.2f} MB)" if tamano_mb else ""
    mensaje = (
        "✅ BACKUP YA REALIZADO HOY\n\n"
        "Base de datos: Bibliouni\n\n"
        f"🕐 Hora del backup: {hora}\n"
        f"📁 Archivo:{tamano_texto}\n"
        f"{ruta}\n\n"
        "El monitoreo está activo. Si no se detecta un backup futuro, "
        "se enviará una alerta a esta hora programada."
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


def _normalizar_comando(texto):
    """
    Normaliza un texto para comparación de comandos:
    - mayúsculas
    - quita acentos
    - reemplaza múltiples espacios/saltos de línea/tab por uno solo
    - elimina espacios al inicio/final
    """
    if not texto:
        return ''
    t = texto.upper().strip()
    t = unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode('ASCII')
    t = re.sub(r'\s+', ' ', t)
    return t


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

    texto_limpio = _normalizar_comando(texto)

    # Validar que el comando sea exacto (permitiendo espacios extra)
    if texto_limpio != "RESUELVE BACKUP":
        print(f"[DEBUG procesar_comando_backup] Comando no reconocido: '{texto_limpio}'")
        return {'processed': False, 'reason': 'Comando no reconocido'}

    # Normalizar ambos números: dejar solo dígitos para evitar fallos por formato
    numero_remoto_normalizado = ''.join(c for c in numero_remoto if c.isdigit())
    numero_destino_normalizado = ''.join(c for c in numero_destino_configurado if c.isdigit())

    # Comparación flexible: en WhatsApp el número puede venir con o sin
    # prefijo de país (ej. 51900685850 vs 900685850). Se comparan los
    # últimos 9 dígitos si ambos tienen al menos 9 dígitos.
    def _ultimos_digitos(numero, n=9):
        return numero[-n:] if len(numero) >= n else numero

    remoto_final = _ultimos_digitos(numero_remoto_normalizado)
    destino_final = _ultimos_digitos(numero_destino_normalizado)

    print(f"[DEBUG procesar_comando_backup] Comparación de números - "
          f"remoto_completo='{numero_remoto_normalizado}', destino_completo='{numero_destino_normalizado}', "
          f"remoto_ultimos9='{remoto_final}', destino_ultimos9='{destino_final}'")

    # Validar que el remitente sea el número destino configurado
    if remoto_final != destino_final:
        print(f"[DEBUG procesar_comando_backup] Número no autorizado: '{numero_remoto_normalizado}' != '{numero_destino_normalizado}'")
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
