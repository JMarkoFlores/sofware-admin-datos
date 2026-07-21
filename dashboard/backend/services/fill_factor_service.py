"""
Servicio de Factor de Llenado (Fill Factor) para Bibliouni.
============================================================

Permite reconstruir los índices de todas las tablas de usuario
en la base de datos Bibliouni con un factor de llenado especificado,
ejecutado mediante un comando recibido por WhatsApp.

¿Qué es el Fill Factor?
-----------------------
El factor de llenado define qué porcentaje de cada página de índice
se llena con datos al reconstruir los índices. Dejar espacio libre
reduce los page splits y mejora el rendimiento de escritura.

Ejemplo de uso desde WhatsApp:
    Usuario envía: "FACTOR LLENADO 80"
    Sistema ejecuta: ALTER INDEX ALL ON [tabla] REBUILD WITH (FILLFACTOR=80)
    Sistema responde por WhatsApp con el resultado.
"""

import pyodbc
from datetime import datetime
from config.settings import Config
from utils.helpers import log_auditoria
from whatsapp import send_message


# ---------------------------------------------------------------------------
# Conexión a Bibliouni (pyodbc directo, igual que backup_service)
# ---------------------------------------------------------------------------

def _get_connection_string():
    """Cadena de conexión pyodbc directamente a Bibliouni."""
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


# ---------------------------------------------------------------------------
# Obtener tablas de usuario
# ---------------------------------------------------------------------------

def obtener_tablas_usuario():
    """
    Lista las tablas de usuario en Bibliouni (schema dbo).

    Returns:
        list: Lista de nombres de tabla, o lista vacía si hay error.
    """
    conn_str = _get_connection_string()
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
            print(f"[DEBUG FillFactor] Tablas encontradas: {tablas}")
            return tablas
    except Exception as e:
        print(f"[ERROR FillFactor] No se pudieron obtener tablas: {e}")
        return []


# ---------------------------------------------------------------------------
# Ejecutar rebuild de índices
# ---------------------------------------------------------------------------

def ejecutar_rebuild_indices(fill_factor):
    """
    Reconstruye TODOS los índices de cada tabla de usuario en Bibliouni
    con el fill factor indicado, mediante el Stored Procedure
    dbo.sp_ejecutar_rebuild_indices.

    Args:
        fill_factor (int): Porcentaje de llenado (1-100).

    Returns:
        dict: {
            'exito': bool,
            'tablas_procesadas': int,
            'tablas_con_error': list,
            'mensaje': str
        }
    """
    print(f"[DEBUG FillFactor] Llamando a sp_ejecutar_rebuild_indices con FILLFACTOR={fill_factor}...")

    conn_str = _get_connection_string()
    try:
        with pyodbc.connect(conn_str, timeout=300, autocommit=True) as conn:
            cursor = conn.cursor()
            # Llamar al Stored Procedure — retorna (tablas_procesadas, tablas_con_error, fill_factor_aplicado)
            cursor.execute("{CALL dbo.sp_ejecutar_rebuild_indices (?)}", fill_factor)
            row = cursor.fetchone()

            tablas_procesadas = int(row[0]) if row else 0
            tablas_con_error  = int(row[1]) if row else 0
            exito = tablas_procesadas > 0 and tablas_con_error == 0

            if exito:
                mensaje = (
                    f"Rebuild completado exitosamente. "
                    f"{tablas_procesadas} tablas procesadas con FILLFACTOR={fill_factor}."
                )
            elif tablas_procesadas > 0:
                mensaje = (
                    f"Rebuild completado con advertencias. "
                    f"{tablas_procesadas} tablas OK, {tablas_con_error} con errores."
                )
            else:
                mensaje = "Rebuild falló. No se procesó ninguna tabla correctamente."

            print(f"[DEBUG FillFactor] Resultado SP: procesadas={tablas_procesadas}, errores={tablas_con_error}")
            return {
                'exito': exito or tablas_procesadas > 0,
                'tablas_procesadas': tablas_procesadas,
                'tablas_con_error': [],   # El SP no retorna detalle por tabla, solo el conteo
                'mensaje': mensaje
            }

    except Exception as e_conn:
        print(f"[DEBUG FillFactor] ERROR al llamar al SP: {e_conn}")
        return {
            'exito': False,
            'tablas_procesadas': 0,
            'tablas_con_error': [],
            'mensaje': f'Error al ejecutar sp_ejecutar_rebuild_indices: {str(e_conn)}'
        }


# ---------------------------------------------------------------------------
# Mensajes de WhatsApp
# ---------------------------------------------------------------------------

def enviar_confirmacion_fill_factor(numero_destino, fill_factor, tablas_procesadas, tablas_con_error):
    """Envía confirmación de rebuild exitoso por WhatsApp."""
    errores_texto = ""
    if tablas_con_error:
        nombres = ", ".join([e['tabla'] for e in tablas_con_error])
        errores_texto = f"\n⚠️ Tablas con error:\n{nombres}\n"

    mensaje = (
        f"✅ FACTOR DE LLENADO APLICADO\n\n"
        f"Base de datos: Bibliouni\n\n"
        f"Configuración:\n"
        f"🔧 Fill Factor: {fill_factor}%\n\n"
        f"Resultado:\n"
        f"📊 Tablas procesadas: {tablas_procesadas}\n"
        f"{errores_texto}\n"
        f"Los índices han sido reconstruidos correctamente."
    )
    return send_message(mensaje, numero_destino)


def enviar_error_fill_factor(numero_destino, detalle_error):
    """Envía notificación de error al aplicar fill factor por WhatsApp."""
    mensaje = (
        f"❌ ERROR - FACTOR DE LLENADO\n\n"
        f"No fue posible reconstruir los índices de Bibliouni.\n\n"
        f"Detalle:\n{detalle_error}\n\n"
        f"Revise los logs del sistema para más información."
    )
    return send_message(mensaje, numero_destino)


def enviar_uso_fill_factor(numero_destino):
    """Envía instrucciones de uso del comando fill factor por WhatsApp."""
    mensaje = (
        f"ℹ️ USO INCORRECTO - FACTOR DE LLENADO\n\n"
        f"Formato correcto:\n"
        f"FACTOR LLENADO <porcentaje>\n\n"
        f"Ejemplos:\n"
        f"• FACTOR LLENADO 80\n"
        f"• FACTOR LLENADO 90\n"
        f"• FACTOR LLENADO 70\n\n"
        f"El porcentaje debe ser un número entre 1 y 100."
    )
    return send_message(mensaje, numero_destino)


# ---------------------------------------------------------------------------
# Procesador principal del comando
# ---------------------------------------------------------------------------

def procesar_comando_fill_factor(texto, numero_remoto, numero_destino_configurado):
    """
    Procesa el comando FACTOR LLENADO <N> recibido por WhatsApp.

    El comando debe tener exactamente el formato:
        FACTOR LLENADO <porcentaje>
    donde <porcentaje> es un número entero entre 1 y 100.

    Args:
        texto (str): Texto del mensaje entrante (sin normalizar).
        numero_remoto (str): Número del remitente (limpio, sin @s.whatsapp.net).
        numero_destino_configurado (str): Número configurado en el sistema.

    Returns:
        dict: Resultado del procesamiento.
    """
    print(f"[DEBUG FillFactor] Iniciando procesamiento...")
    print(f"[DEBUG FillFactor] texto='{texto}', remoto='{numero_remoto}', destino='{numero_destino_configurado}'")

    texto_limpio = texto.strip().upper()
    partes = texto_limpio.split()

    # Validar estructura: debe ser ["FACTOR", "LLENADO", "<N>"]
    if len(partes) != 3 or partes[0] != "FACTOR" or partes[1] != "LLENADO":
        print(f"[DEBUG FillFactor] Formato incorrecto: '{texto_limpio}'")
        enviar_uso_fill_factor(numero_destino_configurado)
        return {'procesado': False, 'razon': 'Formato de comando incorrecto'}

    # Validar que el porcentaje sea numérico y esté en rango
    try:
        fill_factor = int(partes[2])
    except ValueError:
        print(f"[DEBUG FillFactor] Porcentaje no es número: '{partes[2]}'")
        enviar_uso_fill_factor(numero_destino_configurado)
        return {'procesado': False, 'razon': 'El porcentaje no es un número válido'}

    if not (1 <= fill_factor <= 100):
        print(f"[DEBUG FillFactor] Porcentaje fuera de rango: {fill_factor}")
        enviar_uso_fill_factor(numero_destino_configurado)
        return {'procesado': False, 'razon': f'Porcentaje fuera de rango: {fill_factor}. Debe ser entre 1 y 100.'}

    # Validar que el remitente sea el número autorizado
    if numero_remoto != numero_destino_configurado:
        print(f"[DEBUG FillFactor] Número no autorizado: {numero_remoto} != {numero_destino_configurado}")
        return {'procesado': False, 'razon': 'Número no autorizado'}

    print(f"[DEBUG FillFactor] Comando y número validados. Fill factor={fill_factor}")

    # Registrar inicio en auditoría
    try:
        log_auditoria(
            'FILL_FACTOR',
            'Índices',
            f'Comando FACTOR LLENADO {fill_factor} recibido. Iniciando rebuild...',
            usuario='sistema',
            resultado='En progreso',
            detalle=f'Origen: {numero_remoto}'
        )
        print(f"[DEBUG FillFactor] Auditoría (inicio) registrada.")
    except Exception as e:
        print(f"[DEBUG FillFactor] ERROR al registrar auditoría (inicio): {e}")

    # Ejecutar rebuild
    print(f"[DEBUG FillFactor] Llamando a ejecutar_rebuild_indices({fill_factor})...")
    resultado = ejecutar_rebuild_indices(fill_factor)
    print(f"[DEBUG FillFactor] Resultado: exito={resultado['exito']}, msg={resultado['mensaje']}")

    if resultado['exito']:
        enviar_confirmacion_fill_factor(
            numero_destino_configurado,
            fill_factor,
            resultado['tablas_procesadas'],
            resultado['tablas_con_error']
        )
        try:
            log_auditoria(
                'FILL_FACTOR',
                'Índices',
                resultado['mensaje'],
                usuario='sistema',
                resultado='Éxito',
                detalle=f'Fill factor={fill_factor}, tablas={resultado["tablas_procesadas"]}'
            )
            print(f"[DEBUG FillFactor] Auditoría (éxito) registrada.")
        except Exception as e:
            print(f"[DEBUG FillFactor] ERROR al registrar auditoría (éxito): {e}")
        return {
            'procesado': True,
            'exito': True,
            'fill_factor': fill_factor,
            'tablas_procesadas': resultado['tablas_procesadas'],
            'mensaje': resultado['mensaje']
        }
    else:
        enviar_error_fill_factor(numero_destino_configurado, resultado['mensaje'])
        try:
            log_auditoria(
                'ERROR',
                'Índices',
                resultado['mensaje'],
                usuario='sistema',
                resultado='Fallo',
                detalle=f'Fill factor={fill_factor}, origen={numero_remoto}'
            )
            print(f"[DEBUG FillFactor] Auditoría (fallo) registrada.")
        except Exception as e:
            print(f"[DEBUG FillFactor] ERROR al registrar auditoría (fallo): {e}")
        return {
            'procesado': True,
            'exito': False,
            'fill_factor': fill_factor,
            'mensaje': resultado['mensaje']
        }


# ---------------------------------------------------------------------------
# Monitoreo de fragmentación de índices
# ---------------------------------------------------------------------------

def verificar_fragmentacion(umbral=30):
    """
    Verifica el nivel de fragmentación de los índices en Bibliouni
    mediante el Stored Procedure dbo.sp_verificar_fragmentacion.

    Args:
        umbral (int): Porcentaje mínimo de fragmentación para considerar
                      que un índice necesita atención (default: 30%).

    Returns:
        dict: {
            'hay_alerta': bool,
            'umbral': int,
            'tablas_fragmentadas': [
                {'tabla': str, 'indice': str, 'fragmentacion': float, 'paginas': int}
            ],
            'total_indices': int,
            'mensaje': str,
            'fecha': str
        }
    """
    conn_str = _get_connection_string()
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        with pyodbc.connect(conn_str, timeout=30) as conn:
            cursor = conn.cursor()
            # Llamar al Stored Procedure con el umbral como parámetro
            cursor.execute("{CALL dbo.sp_verificar_fragmentacion (?)}", umbral)

            fragmentadas = []
            for row in cursor.fetchall():
                fragmentadas.append({
                    'tabla':         row[0],
                    'indice':        row[1] or '(sin nombre)',
                    'fragmentacion': float(row[2]),
                    'paginas':       int(row[3])
                })

            hay_alerta = len(fragmentadas) > 0

            if hay_alerta:
                mensaje = (
                    f"Se encontraron {len(fragmentadas)} índices con fragmentación "
                    f">= {umbral}% en {Config.BIBLIOUNI_DB}."
                )
            else:
                mensaje = (
                    f"Todos los índices de {Config.BIBLIOUNI_DB} están por debajo "
                    f"del umbral de {umbral}%. No se requiere acción."
                )

            print(f"[DEBUG Fragmentación] {mensaje}")
            return {
                'hay_alerta':          hay_alerta,
                'umbral':              umbral,
                'tablas_fragmentadas': fragmentadas,
                'total_indices':       len(fragmentadas),
                'mensaje':             mensaje,
                'fecha':               fecha
            }

    except Exception as e:
        print(f"[ERROR Fragmentación] {e}")
        return {
            'hay_alerta':          False,
            'umbral':              umbral,
            'tablas_fragmentadas': [],
            'total_indices':       0,
            'mensaje':             f'Error al ejecutar sp_verificar_fragmentacion: {str(e)}',
            'fecha':               fecha
        }


def enviar_alerta_fragmentacion(numero_destino, resultado):
    """
    Envía alerta de fragmentación por WhatsApp con el detalle de
    qué tablas/índices superan el umbral.
    """
    fragmentadas = resultado['tablas_fragmentadas']
    umbral = resultado['umbral']

    # Listar las tablas fragmentadas (máximo 10 para no hacer un mensaje enorme)
    detalle_lineas = []
    for item in fragmentadas[:10]:
        detalle_lineas.append(
            f"  - {item['tabla']}.{item['indice']}: "
            f"{item['fragmentacion']:.1f}% ({item['paginas']} págs)"
        )
    if len(fragmentadas) > 10:
        detalle_lineas.append(f"  ... y {len(fragmentadas) - 10} índices más.")

    detalle = "\n".join(detalle_lineas)

    mensaje = (
        f"🚨 ALERTA DE FRAGMENTACIÓN\n\n"
        f"Base de datos: {Config.BIBLIOUNI_DB}\n"
        f"Umbral configurado: {umbral}%\n\n"
        f"Se detectaron {len(fragmentadas)} índices fragmentados:\n\n"
        f"{detalle}\n\n"
        f"Para optimizar los índices, responda con:\n\n"
        f"FACTOR LLENADO 80"
    )
    return send_message(mensaje, numero_destino)


def enviar_ok_fragmentacion(numero_destino, resultado):
    """Envía confirmación de que la fragmentación está dentro del umbral."""
    mensaje = (
        f"✅ FRAGMENTACIÓN OK\n\n"
        f"Base de datos: {Config.BIBLIOUNI_DB}\n"
        f"Umbral configurado: {resultado['umbral']}%\n\n"
        f"Todos los índices ({resultado['total_indices']}) están por debajo "
        f"del umbral. No se requiere acción."
    )
    return send_message(mensaje, numero_destino)
