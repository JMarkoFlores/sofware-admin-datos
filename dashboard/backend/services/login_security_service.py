"""
Servicio de monitoreo de seguridad de login para SQL Server.
===================================================================

- Crea una tabla de auditoría para logins fallidos en SQL Server
- MONITOREO DUAL:
  1. Tabla AuditoriaLoginsFallidos (si el trigger está instalado)
  2. Log de errores de SQL Server (xp_readerrorlog, para capturar Error 18456 directamente)
- Envía alertas por WhatsApp y espera comando BLOQUEA para deshabilitar login
- Usa la misma estructura que backup_service.py
- [DEBUG] Tiene logs extensivos para diagnosticar cualquier problema
"""

import os
import pyodbc
import re
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import log_auditoria
from whatsapp import send_message

# Variables globales de estado (igual que backup_service)
failed_attempts = {}
pending_alerts = {}
last_processed_log_id = 0  # Para evitar re-procesar registros de la tabla
last_processed_error_time = None  # Para evitar re-procesar entradas del log de errores
current_pending_alert_username = None


def _get_sql_server_connection_string():
    """Cadena de conexión a SQL Server master (para ejecutar comandos de seguridad)."""
    if Config.BIBLIOUNI_TRUSTED == 'yes':
        conn_str = (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=master;"
            f"Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{{Config.BIBLIOUNI_DRIVER}}};"
            f"SERVER={Config.BIBLIOUNI_SERVER};"
            f"DATABASE=master;"
            f"UID={Config.BIBLIOUNI_USER};"
            f"PWD={Config.BIBLIOUNI_PASSWORD};"
        )
    print(f"[DEBUG SEGURO] Cadena de conexión construida: {conn_str.replace(Config.BIBLIOUNI_PASSWORD, '****') if hasattr(Config, 'BIBLIOUNI_PASSWORD') else conn_str}")
    return conn_str


def _initialize_audit_table():
    """Crea la tabla de auditoría para logins fallidos si no existe (en la base de datos master)."""
    print("[DEBUG SEGURO] Verificando/creando la tabla AuditoriaLoginsFallidos en master...")
    conn_str = _get_sql_server_connection_string()

    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuditoriaLoginsFallidos')
                BEGIN
                    CREATE TABLE AuditoriaLoginsFallidos (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        username NVARCHAR(128) NOT NULL,
                        fecha_hora DATETIME DEFAULT GETDATE(),
                        ip NVARCHAR(50),
                        mensaje NVARCHAR(MAX)
                    );
                    PRINT 'Tabla AuditoriaLoginsFallidos creada exitosamente';
                END
                ELSE
                BEGIN
                    PRINT 'Tabla AuditoriaLoginsFallidos ya existe';
                END
            """)

        print(f"[DEBUG SEGURO] [OK] Tabla AuditoriaLoginsFallidos verificada/creada correctamente en master")
    except Exception as e:
        print(f"[DEBUG SEGURO] ERROR CRÍTICO al crear/verificar la tabla de auditoría: {str(e)}")
        import traceback
        print(f"[DEBUG SEGURO] Stacktrace completo:\n{traceback.format_exc()}")


def _get_new_logins_from_table():
    """Obtiene nuevos registros de logins fallidos de la tabla AuditoriaLoginsFallidos."""
    global last_processed_log_id
    new_entries = []

    print(f"[DEBUG SEGURO] (Método 1) Consultando tabla AuditoriaLoginsFallidos para registros con id > {last_processed_log_id}...")
    conn_str = _get_sql_server_connection_string()

    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, fecha_hora 
                FROM AuditoriaLoginsFallidos 
                WHERE id > ?
                ORDER BY id ASC
            """, (last_processed_log_id,))

            for row in cursor.fetchall():
                entry = {
                    'id': row[0],
                    'username': row[1],
                    'fecha_hora': row[2] if isinstance(row[2], datetime) else datetime.now()
                }
                new_entries.append(entry)
                if entry['id'] > last_processed_log_id:
                    last_processed_log_id = entry['id']

            if new_entries:
                print(f"[DEBUG SEGURO] (Método 1) [OK] Encontrados {len(new_entries)} registros nuevos en la tabla!")
                for entry in new_entries:
                    print(f"[DEBUG SEGURO]    -> Tabla: id={entry['id']}, Usuario={entry['username']}, Fecha={entry['fecha_hora']}")
            else:
                print(f"[DEBUG SEGURO] (Método 1) No hay registros nuevos en la tabla.")

    except Exception as e:
        print(f"[DEBUG SEGURO] (Método 1) ERROR al consultar la tabla: {str(e)}")
        import traceback
        print(f"[DEBUG SEGURO] (Método 1) Stacktrace:\n{traceback.format_exc()}")

    return new_entries


def _parse_username_from_error_message(text):
    """Extrae el nombre de usuario del mensaje de error 18456."""
    # Patrones comunes para encontrar el usuario en el mensaje de error
    patterns = [
        r"user\s+'([^']+)'",
        r"login\s+'([^']+)'",
        r"for user '([^']+)'",
        r"Login failed for user '([^']+)'",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _get_new_logins_from_error_log():
    """Obtiene nuevos registros de logins fallidos directamente del log de errores de SQL Server (xp_readerrorlog)."""
    global last_processed_error_time
    new_entries = []

    print(f"[DEBUG SEGURO] (Método 2) Consultando log de errores de SQL Server para Error 18456...")
    conn_str = _get_sql_server_connection_string()

    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()

            # Leer el log de errores actual, filtrando por 'Login failed'
            # Simplified call to xp_readerrorlog to avoid parameter errors
            cursor.execute("EXEC xp_readerrorlog 0, 1")

            # Establecer tiempo mínimo si no hay uno (últimos 30 minutos)
            if last_processed_error_time is None:
                last_processed_error_time = datetime.now() - timedelta(minutes=30)
                print(f"[DEBUG SEGURO] (Método 2) No hay tiempo de última ejecución, estableciendo a últimos 30 minutos: {last_processed_error_time}")

            for row in cursor.fetchall():
                log_date = row[0]
                process_info = row[1]
                text = row[2]

                # Only process entries that contain 'Login failed'
                if 'Login failed' not in text:
                    continue

                # Convertir log_date a datetime
                log_dt = None
                if isinstance(log_date, datetime):
                    log_dt = log_date
                elif isinstance(log_date, str):
                    # Intentar formatos comunes
                    for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S.%f', '%Y/%m/%d %H:%M:%S']:
                        try:
                            log_dt = datetime.strptime(log_date, fmt)
                            break
                        except:
                            continue

                if log_dt is None:
                    continue  # Saltar si no podemos parsear la fecha

                # Saltar entradas ya procesadas
                if log_dt <= last_processed_error_time:
                    continue

                # Extraer username
                username = _parse_username_from_error_message(text)

                if username:
                    entry = {
                        'id': None,
                        'username': username,
                        'fecha_hora': log_dt
                    }
                    new_entries.append(entry)
                    print(f"[DEBUG SEGURO] (Método 2)    -> Log: Usuario={username}, Fecha={log_dt}")

            # Actualizar último tiempo procesado
            if new_entries:
                last_processed_error_time = max([entry['fecha_hora'] for entry in new_entries])
                print(f"[DEBUG SEGURO] (Método 2) [OK] Encontrados {len(new_entries)} registros nuevos en el log de errores!")

            else:
                print(f"[DEBUG SEGURO] (Método 2) No hay registros nuevos en el log de errores.")

    except Exception as e:
        print(f"[DEBUG SEGURO] (Método 2) ERROR al consultar el log de errores (continuando sin él): {str(e)}")

    return new_entries


def track_failed_attempts():
    """
    Actualiza el contador de intentos fallidos usando AMBOS métodos (tabla y log de errores).
    También limpia entradas antiguas (más de 30 minutos).
    """
    global failed_attempts

    print("\n[DEBUG SEGURO] Iniciando track_failed_attempts() con DUAL MONITOREO...")

    # Primero, inicializar la tabla si es necesario
    _initialize_audit_table()

    # Obtener registros de AMBOS métodos
    entries_table = _get_new_logins_from_table()
    entries_error_log = _get_new_logins_from_error_log()
    all_entries = entries_table + entries_error_log

    if not all_entries:
        print(f"[DEBUG SEGURO] No hay nuevos intentos fallidos de ningún método.")
    else:
        print(f"[DEBUG SEGURO] Procesando {len(all_entries)} intentos fallidos en total...")

    # Actualizar el contador para cada usuario
    for entry in all_entries:
        username = entry['username']

        if username not in failed_attempts:
            failed_attempts[username] = {
                'count': 0,
                'last_attempt': entry['fecha_hora']
            }
            print(f"[DEBUG SEGURO] Nuevo usuario agregado al contador: {username}")

        failed_attempts[username]['count'] += 1
        failed_attempts[username]['last_attempt'] = entry['fecha_hora']
        print(f"[DEBUG SEGURO] Contador actualizado para {username}: {failed_attempts[username]['count']} intentos (último: {failed_attempts[username]['last_attempt']})")

    # Limpiar entradas antiguas (más de 30 minutos)
    now = datetime.now()
    usernames_to_remove = []
    for username in failed_attempts:
        last_dt = failed_attempts[username]['last_attempt']
        if (now - last_dt).total_seconds() > 1800:  # 30 minutos = 1800 segundos
            usernames_to_remove.append(username)

    for username in usernames_to_remove:
        del failed_attempts[username]
        print(f"[DEBUG SEGURO] Eliminado contador antiguo para {username} (superó los 30 minutos)")


def check_failed_attempts(destination):
    """
    Verifica si algún usuario ha superado el límite de intentos fallidos y envía alerta si es necesario.
    Devuelve un diccionario con información sobre la alerta (si se envió).
    """
    global pending_alerts, current_pending_alert_username

    print("\n[DEBUG SEGURO] =======================================")
    print("[DEBUG SEGURO] Iniciando verificación de Logins fallidos en SQL Server...")

    # Actualizar contadores primero
    track_failed_attempts()

    print(f"[DEBUG SEGURO] Estado actual del contador global failed_attempts: {failed_attempts}")
    print(f"[DEBUG SEGURO] Estado actual de pending_alerts: {pending_alerts}")
    print(f"[DEBUG SEGURO] Estado de current_pending_alert_username: {current_pending_alert_username}")

    alert_info = None

    # Verificar si algún usuario tiene más de 2 intentos fallidos y no tiene alerta pendiente
    for username in failed_attempts:
        count = failed_attempts[username]['count']
        print(f"[DEBUG SEGURO] Revisando usuario: {username}, Intentos totales: {count}")

        if count > 2 and username not in pending_alerts:
            print(f"[DEBUG SEGURO] ¡Se encontraron fallos! Usuario: {username}, Intentos detectados: {count}")

            # Almacenar la alerta pendiente
            pending_alerts[username] = {
                'timestamp': datetime.now(),
                'count': count,
                'notified': False
            }
            current_pending_alert_username = username
            print(f"[DEBUG SEGURO] Alerta pendiente agregada para {username}, marcada como 'notified: False'")

            # Enviar alerta por WhatsApp
            print(f"[DEBUG SEGURO] Intentando enviar mensaje usando el servicio común de la app al número: {destination}")
            send_result = send_login_alert(username, count, destination)

            # Registrar en auditoría (ignore if no app context)
            try:
                log_auditoria(
                    'ALERTA',
                    'Seguridad Login',
                    f'Se detectaron {count} intentos fallidos para el usuario {username}',
                    usuario='sistema',
                    resultado='Alerta'
                )
                print(f"[DEBUG SEGURO] Auditoría registrada exitosamente")
            except Exception as e:
                print(f"[DEBUG SEGURO] No se pudo registrar en auditoría (no app context?): {e}")

            # Guardar información de la alerta
            alert_info = {
                'username': username,
                'count': count,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'destination': destination,
                'sent': send_result
            }

    print("[DEBUG SEGURO] =======================================\n")
    return alert_info


def send_login_alert(username, attempts, destination):
    """Envía alerta por WhatsApp con el formato de criticidad alta (igual que backup_service).
    Devuelve True si la alerta se envió correctamente, False en caso contrario."""
    print(f"[DEBUG SEGURO] Construyendo mensaje de alerta para {destination}...")
    mensaje = (
        "⚠️ ALERTA: POSIBLE AMENAZA\n\n"
        f"El usuario {username} ha fallado su contraseña {attempts} veces en los últimos 30 minutos.\n\n"
        "Para deshabilitar inmediatamente este login responde:\n\n"
        "BLOQUEA"
    )
    print(f"[DEBUG SEGURO] Mensaje construido")

    print(f"[DEBUG SEGURO] Llamando a send_message() del servicio común...")
    result = send_message(mensaje, destination)
    print(f"[DEBUG SEGURO] Resultado de send_message(): {result}")

    if result['success']:
        pending_alerts[username]['notified'] = True
        print(f"[DEBUG SEGURO] [OK] Alerta enviada correctamente a {destination} para {username}")
        return True
    else:
        print(f"[DEBUG SEGURO] [ERROR] ERROR al enviar alerta: {result.get('error', 'Error desconocido')}")
        return False


def disable_login(username):
    """Deshabilita un login de SQL Server usando el Procedimiento Almacenado sp_BloquearUsuarioLogin."""
    print(f"[DEBUG SEGURO] Intentando deshabilitar login {username} en SQL Server usando sp_BloquearUsuarioLogin...")
    conn_str = _get_sql_server_connection_string()

    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            conn.autocommit = True
            cursor = conn.cursor()

            # Ejecutar el Procedimiento Almacenado
            print(f"[DEBUG SEGURO] Ejecutando: EXEC dbo.sp_BloquearUsuarioLogin @LoginName = ?;")
            cursor.execute("EXEC dbo.sp_BloquearUsuarioLogin @LoginName = ?;", (username,))
            print(f"[DEBUG SEGURO] [OK] Procedimiento Almacenado ejecutado exitosamente")

            # Registrar en auditoría
            try:
                log_auditoria(
                    'BLOQUEO',
                    'Seguridad Login',
                    f'Login {username} deshabilitado exitosamente via sp_BloquearUsuarioLogin',
                    usuario='sistema',
                    resultado='Éxito'
                )
                print(f"[DEBUG SEGURO] Auditoría registrada exitosamente")
            except Exception as e:
                print(f"[DEBUG SEGURO] ERROR al registrar auditoría: {e}")

            return {
                'exito': True,
                'mensaje': f'Login {username} deshabilitado exitosamente via Procedimiento Almacenado'
            }

    except Exception as e:
        print(f"[DEBUG SEGURO] ERROR CRÍTICO al bloquear login {username}: {str(e)}")
        import traceback
        print(f"[DEBUG SEGURO] Stacktrace completo:\n{traceback.format_exc()}")
        try:
            log_auditoria(
                'ERROR',
                'Seguridad Login',
                f'Error al bloquear login {username} via sp_BloquearUsuarioLogin: {str(e)}',
                usuario='sistema',
                resultado='Fallo'
            )
        except Exception as e_audit:
            print(f"[DEBUG SEGURO] ERROR adicional al registrar auditoría: {e_audit}")
        return {
            'exito': False,
            'mensaje': f'Error al bloquear login via Procedimiento Almacenado: {str(e)}'
        }


def send_confirmation_bloqueo(numero_destino, username):
    """Envía confirmación de que el login fue bloqueado exitosamente."""
    print(f"[DEBUG SEGURO] Enviando confirmación de bloqueo a {numero_destino}...")
    mensaje = (
        f"✅ LOGIN DESHABILITADO\n\n"
        f"El login {username} ha sido deshabilitado exitosamente.\n"
    )
    result = send_message(mensaje, numero_destino)
    print(f"[DEBUG SEGURO] Resultado de confirmación de bloqueo: {result}")
    return result


def send_error_bloqueo(numero_destino, username, mensaje_error):
    """Envía notificación de error al intentar bloquear un login."""
    print(f"[DEBUG SEGURO] Enviando notificación de error de bloqueo a {numero_destino}...")
    mensaje = (
        f"❌ ERROR AL DESHABILITAR LOGIN\n\n"
        f"No fue posible deshabilitar el login {username}:\n\n"
        f"{mensaje_error}"
    )
    result = send_message(mensaje, numero_destino)
    print(f"[DEBUG SEGURO] Resultado de notificación de error: {result}")
    return result


def procesar_comando_login(texto, numero_remoto, numero_destino_configurado):
    """
    Procesa el comando BLOQUEA recibido por WhatsApp para deshabilitar un login.
    Siguiendo el mismo patrón que procesar_comando_backup en backup_service.py.
    """
    global pending_alerts, current_pending_alert_username

    print("\n[DEBUG SEGURO] =======================================")
    print(f"[DEBUG SEGURO] procesar_comando_login() ejecutado!")
    print(f"[DEBUG SEGURO]    texto recibido: '{texto}'")
    print(f"[DEBUG SEGURO]    numero_remoto: '{numero_remoto}'")
    print(f"[DEBUG SEGURO]    numero_destino_configurado: '{numero_destino_configurado}'")

    texto_limpio = texto.strip().upper()

    # Validar que el comando sea exactamente BLOQUEA
    if texto_limpio != "BLOQUEA":
        print(f"[DEBUG SEGURO] Comando NO reconocido: '{texto_limpio}' (se esperaba 'BLOQUEA')")
        return {'procesado': False, 'razon': 'Comando no reconocido'}
    print(f"[DEBUG SEGURO] [OK] Comando 'BLOQUEA' reconocido correctamente")

    # Validar que el remitente sea el número destino configurado
    if numero_remoto != numero_destino_configurado:
        print(f"[DEBUG SEGURO] [ERROR] Número no autorizado: '{numero_remoto}' != '{numero_destino_configurado}'")
        return {'procesado': False, 'razon': 'Número no autorizado'}
    print(f"[DEBUG SEGURO] [OK] Número autorizado correctamente")

    # Validar que haya una alerta pendiente para bloquear
    if not pending_alerts:
        print(f"[DEBUG SEGURO] [ERROR] No hay alertas pendientes para bloquear")
        send_message("No hay alertas de seguridad de login pendientes para bloquear.", numero_remoto)
        return {'procesado': True, 'razon': 'No hay alertas pendientes'}

    # Obtener el username a bloquear (usamos el último con alerta pendiente)
    if current_pending_alert_username and current_pending_alert_username in pending_alerts:
        username = current_pending_alert_username
    else:
        # Si no, usamos el primero en la lista
        username = next(iter(pending_alerts.keys()))

    print(f"[DEBUG SEGURO] Usuario a bloquear seleccionado: {username}")

    # Ejecutar bloqueo
    resultado = disable_login(username)

    if resultado['exito']:
        # Limpiar la alerta pendiente y el username pendiente
        del pending_alerts[username]
        current_pending_alert_username = None
        print(f"[DEBUG SEGURO] [OK] Alerta pendiente limpiada para {username}")

        # Enviar confirmación
        send_confirmation_bloqueo(numero_destino_configurado, username)

        print(f"[DEBUG SEGURO] [OK] Bloqueo completado exitosamente para {username}")
        print("[DEBUG SEGURO] =======================================\n")
        return {'procesado': True, 'exito': True, 'mensaje': resultado['mensaje']}
    else:
        # Enviar error
        send_error_bloqueo(numero_destino_configurado, username, resultado['mensaje'])

        print(f"[DEBUG SEGURO] [ERROR] Bloqueo fallido para {username}: {resultado['mensaje']}")
        print("[DEBUG SEGURO] =======================================\n")
        return {'procesado': True, 'exito': False, 'mensaje': resultado['mensaje']}


def simulate_failed_login(username):
    """
    Inserta un registro de login fallido en la tabla de auditoría para pruebas.
    Útil para probar el sistema sin tener que fallar credenciales reales.
    """
    print(f"\n[DEBUG SEGURO] =======================================")
    print(f"[DEBUG SEGURO] simulate_failed_login() ejecutado para usuario: {username}")
    conn_str = _get_sql_server_connection_string()

    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            conn.autocommit = True
            cursor = conn.cursor()

            print(f"[DEBUG SEGURO] Insertando registro en AuditoriaLoginsFallidos...")
            cursor.execute("""
                INSERT INTO AuditoriaLoginsFallidos (username, mensaje)
                VALUES (?, 'Intento fallido simulado para pruebas')
            """, (username,))

        print(f"[DEBUG SEGURO] [OK] Registro insertado exitosamente para {username}")
        print("[DEBUG SEGURO] =======================================\n")
        return {
            'exito': True,
            'mensaje': f'Simulado intento fallido para {username}'
        }
    except Exception as e:
        print(f"[DEBUG SEGURO] ERROR CRÍTICO al simular intento fallido: {str(e)}")
        import traceback
        print(f"[DEBUG SEGURO] Stacktrace completo:\n{traceback.format_exc()}")
        print("[DEBUG SEGURO] =======================================\n")
        return {
            'exito': False,
            'mensaje': f'Error al simular intento fallido: {str(e)}'
        }
