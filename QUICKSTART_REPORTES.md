🚀 GUÍA RÁPIDA DE INICIO - Reportes por WhatsApp
════════════════════════════════════════════════════════════════

1️⃣ INICIALIZAR LA BASE DE DATOS

Abre una terminal en: dashboard/backend/

  python database/init_db.py

Esto creará la tabla 'user_conversations' necesaria para persistir
el estado de las conversaciones.

════════════════════════════════════════════════════════════════

2️⃣ INICIAR EL BACKEND

Desde la carpeta dashboard/backend/:

  python app.py

Deberías ver:
  ============================================================
    SISTEMA DE BIBLIOTECA UNIVERSITARIA - BACKEND
  ============================================================
    API: http://localhost:5000
    Bibliouni: (local)/Bibliouni
    TenebrosaOLTP: (local)/TenebrosaOLTP
    Evolution API: http://localhost:8081
  ============================================================

════════════════════════════════════════════════════════════════

3️⃣ INICIAR EL FRONTEND

Abre otra terminal en: dashboard/frontend/

  npm run dev

Deberías ver:
  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help

════════════════════════════════════════════════════════════════

4️⃣ ABRIR LA APLICACIÓN

En tu navegador, ve a: http://localhost:5173

Deberías ver el dashboard de Biblioteca Universitaria.

════════════════════════════════════════════════════════════════

5️⃣ ACCEDER AL DISPARADOR

En el menú lateral izquierdo, haz clic en: Disparador

Desplázate hacia abajo hasta la sección:
  📊 Reportes Automáticos

════════════════════════════════════════════════════════════════

6️⃣ ACTIVAR REPORTES

En la sección "Reportes Automáticos":

  a) Ingresa número de WhatsApp (ej: 51900685850)
  b) Haz clic en: "Iniciar Reportes"
  c) El sistema programará reportes automáticos

Deberías ver:
  ✓ Status cambio a "En ejecución"
  ✓ Próximo reporte diario: 08:00 (o tu hora configurada)
  ✓ Próximo reporte semanal: Lunes 09:00 (o tu horario)

════════════════════════════════════════════════════════════════

7️⃣ PROBAR LOS REPORTES

Mientras los reportes están activos, tienes dos opciones:

OPCIÓN A - Reportes Automáticos Programados:
  a) Haz clic en: "🧪 Prueba Diario"
  b) Un reporte diario se enviará a tu WhatsApp
     (sin esperar a las 08:00 AM)

OPCIÓN B - Reportes Interactivos:
  a) Envía cualquier mensaje a WhatsApp desde el número
     de destino configurado
  b) El sistema mostrará un MENÚ con opciones 1-5
  c) Selecciona un número (ej: "1" para estadísticas)
  d) Recibirás el reporte al instante
  e) Se ofrecerá continuar o cancelar

════════════════════════════════════════════════════════════════

8️⃣ CONFIGURAR HORARIOS (OPCIONAL)

Si quieres cambiar los horarios de reportes automáticos:

Abre: dashboard/backend/.env

Busca estas variables:

  # REPORTES DIARIOS
  REPORTS_DAILY_HOUR=8         ← Cambia a tu hora deseada (0-23)
  REPORTS_DAILY_MINUTE=0       ← Minuto (0-59)
  REPORTS_DAILY_TYPES=estadisticas,multas  ← Tipos de reportes

  # REPORTES SEMANALES
  REPORTS_WEEKLY_DAY=MON       ← Día (MON, TUE, WED, THU, FRI, SAT, SUN)
  REPORTS_WEEKLY_HOUR=9        ← Hora (0-23)
  REPORTS_WEEKLY_MINUTE=0      ← Minuto (0-59)
  REPORTS_WEEKLY_TYPES=estadisticas,libros_prestados,devoluciones_pendientes

  # ZONA HORARIA
  REPORTS_TIMEZONE=America/Lima ← Tu zona horaria

Guarda los cambios y reinicia el backend (Ctrl+C y python app.py)

════════════════════════════════════════════════════════════════

📊 TIPOS DE REPORTES DISPONIBLES

Cuando selecciones un número en el menú interactivo:

  1️⃣ Estadísticas Generales
     → Total libros, disponibles, autores, categorías, lectores, préstamos, multas

  2️⃣ Libros Más Prestados
     → Top 5 de libros más solicitados en la biblioteca

  3️⃣ Multas Pendientes
     → Cantidad y monto total de multas no pagadas

  4️⃣ Préstamos Vencidos
     → Últimos 10 préstamos que se pasaron de la fecha de devolución

  5️⃣ Libros Dañados
     → Reportes de daños registrados en los últimos 30 días

  0️⃣ Cancelar
     → Termina la conversación

════════════════════════════════════════════════════════════════

🧪 FLUJO INTERACTIVO EJEMPLO

TÚ:          "Hola, necesito un reporte"

SISTEMA:     "🎯 MENÚ DE REPORTES - BIBLIOTECA UNIVERSITARIA
              Selecciona el reporte que deseas:
              1. 📊 Estadísticas Generales
              2. 📚 Libros Más Prestados
              3. 💰 Multas Pendientes
              4. ⏰ Préstamos Vencidos
              5. 🔴 Libros Dañados
              0. ❌ Cancelar"

TÚ:          "1"

SISTEMA:     "⏳ Generando reporte, por favor espera..."
             [Envía reporte de estadísticas]
             
             "¿Deseas otro reporte?
              1️⃣ Sí, otro reporte
              2️⃣ No, cancelar"

TÚ:          "2"

SISTEMA:     "✅ Gracias por usar el sistema de reportes. ¡Hasta luego!"

════════════════════════════════════════════════════════════════

⏸️ DETENER REPORTES

Si necesitas detener los reportes automáticos:

  a) Ve a Disparador → Reportes Automáticos
  b) Haz clic en: "Detener"
  c) Los reportes programados se cancelarán

════════════════════════════════════════════════════════════════

🔧 VERIFICAR ESTADO

En cualquier momento, puedes ver el estado actual:

  a) Ve a Disparador → Reportes Automáticos
  b) La UI mostrará:
     - Estado actual (En ejecución / Detenido)
     - Próximo reporte diario (día/hora)
     - Próximo reporte semanal (día/hora)
     - Último reporte enviado

════════════════════════════════════════════════════════════════

⚠️ SOLUCIÓN DE PROBLEMAS

❌ "El reporte no se envía"
  → Verifica que Evolution API está corriendo: docker-compose ps
  → Comprueba el número de WhatsApp en .env
  → Revisa la consola de Flask para errores

❌ "El menú interactivo no responde"
  → Asegúrate de que reportes están activos ("En ejecución")
  → Verifica que el webhook está configurado
  → Prueba con el botón "Prueba Diario" primero

❌ "La conversación no persiste"
  → Ejecuta: python database/init_db.py
  → Verifica que la tabla user_conversations existe
  → Reinicia el backend

════════════════════════════════════════════════════════════════

📚 DOCUMENTACIÓN COMPLETA

Para más detalles, ver: REPORTES_INTERACTIVOS.md

════════════════════════════════════════════════════════════════

🎉 ¡Listo! Ya puedes usar reportes por WhatsApp.

Cualquier pregunta o problema, revisa:
  - Console de Flask (backend)
  - Browser console (frontend)
  - Archivo REPORTES_INTERACTIVOS.md

════════════════════════════════════════════════════════════════
