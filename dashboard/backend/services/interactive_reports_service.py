"""
Servicio para manejar reportes interactivos por WhatsApp.
Gestiona menús, estado de conversación y generación de reportes bajo demanda.
"""

import json
from datetime import datetime
from models.user_conversation import UserConversation
from services.reporte_service import generar_reporte
from utils.helpers import log_auditoria

# Tipos de reportes disponibles para supervisión
REPORT_TYPES = {
    '1': {
        'id': 'estadisticas',
        'nombre': '📊 Estadísticas generales',
        'descripcion': 'Resumen de la biblioteca y métricas clave'
    },
    '2': {
        'id': 'libros_prestados',
        'nombre': '📚 Libros más prestados',
        'descripcion': 'Las obras con más préstamos recientes'
    },
    '3': {
        'id': 'multas',
        'nombre': '💰 Multas pendientes',
        'descripcion': 'Detalle de multas por lector y motivo'
    },
    '4': {
        'id': 'devoluciones_pendientes',
        'nombre': '⏰ Préstamos vencidos',
        'descripcion': 'Préstamos que ya deberían haber sido devueltos'
    },
    '5': {
        'id': 'libros_danios',
        'nombre': '📕 Libros dañados',
        'descripcion': 'Daños recientes reportados en el inventario'
    }
}


def generar_menu_principal():
    """Genera el menú de selección de reportes."""
    msg = """🎯 *MENÚ DE REPORTES - BIBLIOTECA UNIVERSITARIA*

Hola, por favor indica qué reporte deseas realizar. Se enviará un PDF detallado por separado.

"""
    for key, report in REPORT_TYPES.items():
        msg += f"{key}. {report['nombre']}\n"
    
    msg += "\n0. ❌ Cancelar\n\n_Responde con el número de tu opción (1-5)_"
    return msg


def validar_seleccion_reporte(texto):
    """Valida si el texto ingresado es una opción válida."""
    texto_limpio = texto.strip().lower()
    
    # Búsqueda por número
    if texto_limpio in REPORT_TYPES:
        return REPORT_TYPES[texto_limpio]['id']
    
    # Búsqueda por nombre parcial (insensible a mayúsculas)
    for key, report in REPORT_TYPES.items():
        if texto_limpio in report['id'].lower() or \
           texto_limpio in report['nombre'].lower():
            return report['id']
    
    return None


def generar_menu_continuar():
    """Genera el menú después de mostrar un reporte."""
    msg = """

¿Deseas otro reporte?

1️⃣ Sí, otro reporte
2️⃣ No, cancelar

_Responde con 1 o 2_"""
    return msg


def procesar_mensaje_usuario(phone_number, texto_mensaje):
    """
    Procesa un mensaje del usuario y gestiona el flujo de reportes.
    
    Args:
        phone_number: Número de WhatsApp del usuario
        texto_mensaje: Contenido del mensaje
        
    Returns:
        dict: {
            'respuesta': str (mensaje a enviar),
            'estado': str (nuevo estado),
            'tipo_reporte': str or None
        }
    """
    # Obtener o crear conversación
    conv = UserConversation.get_or_create(phone_number)
    
    # Si la sesión expiró, reiniciar y recalcular estado
    if conv.state != 'idle' and not UserConversation.is_session_active(phone_number):
        conv.reset()
    
    estado_actual = conv.state
    texto_limpio = texto_mensaje.strip()
    
    # =====================================================================
    # ESTADO: IDLE (Inicio o sesión completada)
    # =====================================================================
    if estado_actual == 'idle':
        # Mostrar menú principal y pedir selección de reporte
        respuesta = generar_menu_principal()
        conv.update_state('menu')
        return {
            'respuesta': respuesta,
            'estado': 'menu',
            'tipo_reporte': None
        }
    
    # =====================================================================
    # ESTADO: MENU (Usuario viendo opciones)
    # =====================================================================
    elif estado_actual == 'menu':
        # Verificar si es cancelación
        if texto_limpio in ['0', 'cancelar', 'cancel']:
            respuesta = "❌ Operación cancelada. ¡Hasta luego!"
            conv.reset()
            log_auditoria(
                'REPORTE',
                'WhatsApp',
                f'Usuario {phone_number} canceló selección de reportes',
                usuario='whatsapp',
                resultado='Cancelado'
            )
            return {
                'respuesta': respuesta,
                'estado': 'idle',
                'tipo_reporte': None
            }
        
        # Validar selección de reporte
        tipo_reporte = validar_seleccion_reporte(texto_limpio)
        
        if not tipo_reporte:
            respuesta = """❌ Opción no válida.

Por favor responde con un número del 1 al 5:
1. Estadísticas generales
2. Libros más prestados
3. Multas pendientes
4. Préstamos vencidos
5. Libros dañados

O escribe "0" para cancelar."""
            return {
                'respuesta': respuesta,
                'estado': 'menu',
                'tipo_reporte': None
            }
        
        # Generar el reporte
        # Si el reporte requiere parámetros, pedirlos primero
        if tipo_reporte == 'estadisticas':
            # Estadísticas no requiere parámetros, generar directamente
            respuesta = "⏳ Generando reporte, por favor espera..."
            conv.update_state('generating_report', report_type=tipo_reporte)
            return {
                'respuesta': respuesta,
                'estado': 'generating_report',
                'tipo_reporte': tipo_reporte
            }
        else:
            # Pedir parámetros según el tipo de reporte
            if tipo_reporte == 'libros_danios':
                respuesta = """📝 *Configuración de Reporte*

Reporte: Libros Dañados

Por favor ingresa la cantidad de días a considerar (1-365).
Ejemplo: 30

_Envía 0 para usar el valor por defecto (30 días)_"""
            else:
                respuesta = """📝 *Configuración de Reporte*

Reporte: """ + REPORT_TYPES[str(list(REPORT_TYPES.keys())[list(REPORT_TYPES.values()).index(next(r for r in REPORT_TYPES.values() if r['id'] == tipo_reporte))])]['nombre'] + """

Por favor ingresa la cantidad de registros a mostrar (1-100).
Ejemplo: 10

_Envía 0 para usar el valor por defecto (20 registros)_"""
            
            conv.update_state('parametros', report_type=tipo_reporte)
            return {
                'respuesta': respuesta,
                'estado': 'parametros',
                'tipo_reporte': tipo_reporte
            }
    
    # =====================================================================
    # ESTADO: PARAMETROS (Usuario ingresando valor de parámetro)
    # =====================================================================
    elif estado_actual == 'parametros':
        # Verificar si es cancelación
        if texto_limpio in ['0', 'cancelar', 'cancel']:
            # Usar valor por defecto
            tipo_reporte = conv.current_report_type
            respuesta = "⏳ Generando reporte con valores por defecto, por favor espera..."
            conv.update_state('generating_report', report_type=tipo_reporte)
            return {
                'respuesta': respuesta,
                'estado': 'generating_report',
                'tipo_reporte': tipo_reporte
            }
        
        # Intentar parsear el valor ingresado
        try:
            valor = int(texto_limpio)
            tipo_reporte = conv.current_report_type
            
            # Validar rango según el tipo
            if tipo_reporte == 'libros_danios':
                if valor < 1 or valor > 365:
                    respuesta = "❌ Valor inválido. Debe estar entre 1 y 365 días. Intenta de nuevo o envía 0 para usar el valor por defecto."
                    return {
                        'respuesta': respuesta,
                        'estado': 'parametros',
                        'tipo_reporte': tipo_reporte
                    }
            else:
                if valor < 1 or valor > 100:
                    respuesta = "❌ Valor inválido. Debe estar entre 1 y 100 registros. Intenta de nuevo o envía 0 para usar el valor por defecto."
                    return {
                        'respuesta': respuesta,
                        'estado': 'parametros',
                        'tipo_reporte': tipo_reporte
                    }
            
            # Guardar el parámetro en la conversación
            if tipo_reporte == 'libros_danios':
                conv.set_param('dias', valor)
            else:
                conv.set_param('limit', valor)
            
            respuesta = f"⏳ Generando reporte con valor {valor}, por favor espera..."
            conv.update_state('generating_report', report_type=tipo_reporte)
            return {
                'respuesta': respuesta,
                'estado': 'generating_report',
                'tipo_reporte': tipo_reporte
            }
        except ValueError:
            respuesta = "❌ Por favor ingresa un número válido. Intenta de nuevo o envía 0 para usar el valor por defecto."
            return {
                'respuesta': respuesta,
                'estado': 'parametros',
                'tipo_reporte': conv.current_report_type
            }
    
    # =====================================================================
    # ESTADO: GENERATING_REPORT (Reporte en progreso)
    # =====================================================================
    elif estado_actual == 'generating_report':
        # Si el usuario envía algo mientras se genera, ignorar
        respuesta = "⏳ Aún estamos generando tu reporte, por favor espera..."
        return {
            'respuesta': respuesta,
            'estado': 'generating_report',
            'tipo_reporte': conv.current_report_type
        }
    
    # =====================================================================
    # ESTADO: REPORT_READY (Reporte listo, ofreciendo continuar)
    # =====================================================================
    elif estado_actual == 'report_ready':
        if texto_limpio in ['1', 'sí', 'si', 'yes', 'otro']:
            # Mostrar menú nuevamente
            respuesta = generar_menu_principal()
            conv.update_state('menu')
            return {
                'respuesta': respuesta,
                'estado': 'menu',
                'tipo_reporte': None
            }
        elif texto_limpio in ['2', 'no', 'cancelar', 'cancel']:
            respuesta = "✅ Gracias por usar el sistema de reportes. ¡Hasta luego!"
            conv.reset()
            return {
                'respuesta': respuesta,
                'estado': 'idle',
                'tipo_reporte': None
            }
        else:
            respuesta = generar_menu_continuar()
            return {
                'respuesta': respuesta,
                'estado': 'report_ready',
                'tipo_reporte': conv.current_report_type
            }
    
    # Estado desconocido
    conv.reset()
    return {
        'respuesta': generar_menu_principal(),
        'estado': 'menu',
        'tipo_reporte': None
    }


def generar_y_enviar_reporte(phone_number, tipo_reporte, **params):
    """
    Genera un reporte específico y prepara el mensaje para envío.
    
    Args:
        phone_number: Número del usuario
        tipo_reporte: Tipo de reporte a generar
        **params: Parámetros opcionales (limit, dias) - si no se proporcionan, se obtienen de la conversación
        
    Returns:
        dict: {
            'mensaje': str (reporte formateado),
            'tipo': str,
            'exito': bool
        }
    """
    # Obtener parámetros de la conversación si no se proporcionan
    if not params:
        conv = UserConversation.get_or_create(phone_number)
        if tipo_reporte == 'libros_danios':
            dias = conv.get_param('dias', 30)
            params = {'dias': dias}
        elif tipo_reporte != 'estadisticas':
            limit = conv.get_param('limit', 20)
            params = {'limit': limit}
    
    try:
        resultado = generar_reporte(tipo_reporte, **params)
        
        if not resultado.get('exito'):
            return {
                'mensaje': resultado.get('mensaje', '❌ Error al generar reporte. Intenta de nuevo.'),
                'tipo': tipo_reporte,
                'exito': False
            }
        
        log_auditoria(
            'REPORTE',
            'WhatsApp',
            f'Reporte {tipo_reporte} generado para {phone_number}',
            usuario='whatsapp',
            resultado='Éxito',
            detalle=f"Tipo: {resultado['tipo']}, Archivo: {resultado.get('pdf_path')}"
        )
        
        return {
            'mensaje': resultado.get('mensaje', '📄 Reporte preparado.'),
            'tipo': resultado.get('tipo', tipo_reporte),
            'exito': True,
            'pdf_path': resultado.get('pdf_path'),
            'titulo': resultado.get('titulo')
        }
    
    except Exception as e:
        print(f"[ERROR] Error generando reporte: {e}")
        log_auditoria(
            'REPORTE',
            'WhatsApp',
            f'Error al generar {tipo_reporte} para {phone_number}',
            usuario='whatsapp',
            resultado='Fallo',
            detalle=str(e)
        )
        return {
            'mensaje': '❌ Error al generar reporte. Intenta de nuevo.',
            'tipo': tipo_reporte,
            'exito': False
        }


def actualizar_estado_reporte_enviado(phone_number):
    """
    Actualiza el estado del usuario después de enviar el reporte.
    Prepara para la siguiente interacción.
    """
    conv = UserConversation.get_or_create(phone_number)
    conv.update_state('report_ready', report_type=conv.current_report_type)


def obtener_estado_conversacion(phone_number):
    """Obtiene el estado actual de una conversación."""
    conv = UserConversation.get_or_create(phone_number)
    return {
        'phone': phone_number,
        'estado': conv.state,
        'tipo_reporte_actual': conv.current_report_type,
        'ultimo_mensaje': conv.last_message_time.isoformat() if conv.last_message_time else None,
        'sesion_activa': UserConversation.is_session_active(phone_number)
    }
