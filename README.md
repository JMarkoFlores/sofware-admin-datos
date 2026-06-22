# Monitoreo SQL Server + WhatsApp

Aplicación en Python para monitorear una base de datos SQL Server llamada **"tenebrosa"** y enviar reportes automáticos por WhatsApp cada 30 minutos.

---

## Tabla de Contenidos

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Requisitos](#requisitos)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Configuración](#configuración)
5. [Scripts SQL](#scripts-sql)
6. [Explicación de Módulos](#explicación-de-módulos)
7. [Ejecución](#ejecución)
8. [Resolución de Problemas](#resolución-de-problemas)
9. [Notas de Seguridad](#notas-de-seguridad)

---

## Estructura del Proyecto

```
Software-Datos/
├── .env.example                 # Plantilla de configuración
├── .env                         # Archivo de configuración real (no versionar)
├── requirements.txt             # Dependencias de Python
├── README.md                    # Este archivo
├── sql/
│   └── 01_crear_tabla_auditoria.sql
├── logs/
│   └── monitoreo.log            # Generado en ejecución
└── src/
    ├── __init__.py              # (Opcional) Marca el paquete
    ├── config.py                # Carga y validación de .env
    ├── database.py              # Conexión SQL Server + auditoría
    ├── whatsapp.py              # Envío de mensajes (Meta API / Twilio / UZAPI)
    ├── monitor.py               # Lógica de monitoreo
    ├── scheduler.py             # Programación de tareas cada 30 min
    └── main.py                  # Punto de entrada de la aplicación
```

---

## Requisitos

- **Python**: 3.10 o superior
- **SQL Server**: 2016 o superior (con base de datos `tenebrosa` creada)
- **Driver ODBC**: *ODBC Driver 17 for SQL Server* (o 18)
- **Cuenta de WhatsApp Business API**, **Twilio** o **UZAPI** (conecta tu WhatsApp personal vía QR)
- **Sistema operativo**: Windows 10/11 (también funciona en Linux/macOS con ajustes menores)

---

## Instalación Paso a Paso

### 1. Clonar o copiar el proyecto

Descarga los archivos en una carpeta, por ejemplo `C:\MonitoreoDB`.

### 2. Crear entorno virtual

```powershell
# En Windows (PowerShell)
cd C:\MonitoreoDB
python -m venv venv

# Activar entorno
.\venv\Scripts\Activate.ps1
```

```bash
# En Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar el driver ODBC de SQL Server

Abre el **Administrador de Orígenes de Datos ODBC (64 bits)** y verifica que existe:

> `ODBC Driver 17 for SQL Server`

Si no existe, descárgalo desde:  
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### 5. Configurar variables de entorno

Copia el archivo de ejemplo:

```bash
copy .env.example .env
```

Edita `.env` con tus credenciales reales (ver sección [Configuración](#configuración)).

### 6. Ejecutar scripts SQL

Abre **SQL Server Management Studio (SSMS)** o **Azure Data Studio**, conecta a la base de datos `tenebrosa` y ejecuta:

```sql
:sql\01_crear_tabla_auditoria.sql
```

Esto creará la tabla `dbo.MonitoreoAuditoria` y la vista `dbo.vw_ResumenAuditoria`.

### 7. Prueba de ejecución única

```bash
cd src
python main.py --once
```

Si ves en consola el mensaje formateado y la conexión a la base de datos es exitosa, el sistema está listo.

### 8. Ejecutar el monitoreo continuo

```bash
python main.py
```

La aplicación se quedará corriendo indefinidamente, enviando un mensaje cada 30 minutos.

---

## Configuración

### Variables de entorno (.env)

#### SQL Server

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_SERVER` | Servidor SQL Server | `localhost` o `192.168.1.10\INSTANCIA` |
| `DB_NAME` | Base de datos | `tenebrosa` |
| `DB_USER` | Usuario SQL | `sa` |
| `DB_PASSWORD` | Contraseña | `TuContraseñaSegura123` |
| `DB_DRIVER` | Driver ODBC | `ODBC Driver 17 for SQL Server` |
| `DB_TRUSTED_CONNECTION` | Windows Auth | `no` (usar `yes` para SSO) |

#### WhatsApp Business Cloud API (Meta)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `WHATSAPP_PROVIDER` | Proveedor | `whatsapp_business_api` |
| `WHATSAPP_API_URL` | URL base de la API | `https://graph.facebook.com/v18.0` |
| `WHATSAPP_PHONE_NUMBER_ID` | ID del número de teléfono | `123456789012345` |
| `WHATSAPP_ACCESS_TOKEN` | Token de acceso permanente | `EAA...` |
| `WHATSAPP_DESTINATION_PHONE` | Número destino | `5215512345678` (código país + número) |

> Para obtener estos valores, sigue la guía oficial de Meta:  
> https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

#### Twilio (Alternativa)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `WHATSAPP_PROVIDER` | Proveedor | `twilio` |
| `TWILIO_ACCOUNT_SID` | SID de cuenta | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Auth Token | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TWILIO_FROM_NUMBER` | Número sandbox | `whatsapp:+14155238886` |
| `TWILIO_TO_NUMBER` | Número destino | `whatsapp:+5215512345678` |

> Para usar Twilio, también necesitas instalar `twilio`:  
> `pip install twilio`

#### UZAPI (WhatsApp personal via QR)

| Variable | Descripción | Ejemplo | Obligatorio |
|----------|-------------|---------|-------------|
| `WHATSAPP_PROVIDER` | Proveedor | `uzapi` | Si |
| `UZAPI_ENDPOINT` | URL base de la API UZAPI | `https://teste.uzapi.com.br:3333` | Si |
| `UZAPI_TOKEN` | Token de acceso | `xxxx-xxxx-xxxx-xxxx` | Si |
| `UZAPI_SESSION` | Número de sesión | `1` | Si |
| `UZAPI_SESSION_KEY` | Session Key | `1` | Si |
| `UZAPI_DESTINATION_PHONE` | Número destino | `5215512345678` | Si |
| `UZAPI_SEND_PATH` | Path del endpoint de envío | `/api/send-message` | No (default: `/api/send-message`) |
| `UZAPI_PHONE_FIELD` | Nombre del campo "teléfono" en el body | `phone` | No (default: `phone`) |
| `UZAPI_MESSAGE_FIELD` | Nombre del campo "mensaje" en el body | `message` | No (default: `message`) |
| `UZAPI_AUTH_HEADER` | Nombre del header de autorización | `Token` | No (default: `Token`) |

> **¿Cómo conectar UZAPI?**
> 1. Accede a tu panel de UZAPI (ej: `https://teste.uzapi.com.br:3333`)
> 2. Ve a **"Adquirir API"** o **"Disparador"** para generar el Token
> 3. Escanea el QR con tu WhatsApp personal (Configuración > Dispositivos vinculados)
> 4. Una vez que diga **"Status: Conectado"**, copia el Endpoint, Session, Session Key y Token al `.env`
> 5. Configura `WHATSAPP_PROVIDER=uzapi` y el número destino en `UZAPI_DESTINATION_PHONE`

#### Aplicación

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `APP_LOG_LEVEL` | Nivel de logging | `INFO` |
| `APP_LOG_FILE` | Ruta del log | `logs/monitoreo.log` |
| `APP_INTERVAL_MINUTES` | Intervalo en minutos | `30` |
| `APP_TIMEZONE` | Zona horaria | `America/Mexico_City` |
| `AUDIT_TABLE` | Tabla de auditoría | `dbo.MonitoreoAuditoria` |

---

## Scripts SQL

### 1. `01_crear_tabla_auditoria.sql`

Crea:

- **Tabla `dbo.MonitoreoAuditoria`**: almacena cada ejecución del monitoreo.
- **Índices**: en `FechaEjecucion` y `EstadoEnvio` para consultas rápidas.
- **Vista `dbo.vw_ResumenAuditoria`**: resumen por estado de envío.

Esquema de la tabla:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Id` | `INT IDENTITY` | Clave primaria |
| `FechaEjecucion` | `DATETIME2` | Fecha en que se ejecutó el monitoreo |
| `CantidadTablas` | `INT` | Tablas de usuario encontradas |
| `CantidadRegistros` | `BIGINT` | Total de filas en todas las tablas |
| `EstadoEnvio` | `VARCHAR(50)` | `Exitoso`, `Fallido`, `Pendiente` |
| `MensajeError` | `NVARCHAR(MAX)` | Error si aplica |
| `MensajeEnviado` | `NVARCHAR(2000)` | Resumen del mensaje WhatsApp |
| `FechaEnvio` | `DATETIME2` | Fecha/hora de envío del mensaje |
| `ProveedorWhatsApp` | `VARCHAR(100)` | API utilizada |
| `TelefonoDestino` | `VARCHAR(50)` | Número destino |

---

## Explicación de Módulos

### `src/config.py`

- **Responsabilidad**: Cargar y validar todas las variables de entorno desde `.env`.
- **Funciones clave**:
  - `load_config()`: lee el `.env`, valida campos obligatorios y devuelve un `dict` tipado.
  - `setup_logging()`: configura logging dual (archivo + consola) con formato legible.
- **Validaciones**:
  - DB_SERVER y DB_NAME son obligatorios.
  - Si `DB_TRUSTED_CONNECTION=no`, entonces DB_USER y DB_PASSWORD son obligatorios.
  - Valida que el proveedor de WhatsApp sea soportado.
  - Intervalo debe ser entero positivo.

### `src/database.py`

- **Responsabilidad**: Conexión a SQL Server, ejecución de queries y registro de auditoría.
- **Clase `DatabaseManager`**:
  - `_build_connection_string()`: arma la cadena ODBC según autenticación SQL o Windows.
  - `connect()`: abre conexión con `pyodbc` y timeout de 30s.
  - `get_user_tables_count()`: cuenta tablas desde `sys.tables` donde `is_ms_shipped = 0`.
  - `get_total_records()`: suma filas usando `sys.partitions` (más rápido que `COUNT(*)` por tabla).
  - `register_audit()`: inserta un registro en `dbo.MonitoreoAuditoria`.
  - **Context manager**: permite usar `with DatabaseManager(config) as db:` para conexión automática.

### `src/whatsapp.py`

- **Responsabilidad**: Abstracción del envío de mensajes WhatsApp.
- **Clase base `WhatsAppSender`** (abstracta): define la interfaz `send_message()`.
- **`WhatsAppBusinessAPISender`**:
  - Usa `requests` para llamar a `POST /{phone_number_id}/messages` de Meta.
  - Maneja errores HTTP, de red y de la API.
  - Devuelve un `dict` con `success`, `response` y `error`.
- **`TwilioSender`**:
  - Importa `twilio.rest.Client` de forma diferida.
  - Envía mensajes usando la API de Twilio.
- **`UZAPISender`**:
  - Usa `requests` para llamar a `POST {endpoint}/api/send-message` de UZAPI.
  - Soporta configuración flexible: endpoint, token, session, session-key, número destino.
  - Permite personalizar el nombre del header de autorización, el path del endpoint y los campos del body (`phone`, `message`, etc.) por si la API usa una variante diferente.
  - Maneja errores HTTP, de red y generales.
- **`create_sender()`**: factory que devuelve la instancia correcta según `WHATSAPP_PROVIDER` (`whatsapp_business_api`, `twilio`, `uzapi`).

### `src/monitor.py`

- **Responsabilidad**: Orquestar el ciclo de monitoreo.
- **Funciones**:
  - `build_message()`: arma el mensaje exacto con el formato solicitado:
    ```
    ---
    REPORTE AUTOMÁTICO SQL SERVER
    Base de datos: tenebrosa
    Cantidad de tablas: X
    Cantidad total de registros: Y
    Fecha: DD/MM/YYYY HH:MM
    ## Estado: Operativo
    ```
  - `run_monitoring_cycle()`:
    1. Abre conexión a SQL Server.
    2. Obtiene métricas.
    3. Genera el mensaje.
    4. Envía por WhatsApp.
    5. Registra auditoría.
    6. Cierra conexión.
    - Si falla el envío, aún registra el fallo en auditoría.
    - Si falla la auditoría, no interrumpe el flujo (solo loguea el error).

### `src/scheduler.py`

- **Responsabilidad**: Programar la ejecución periódica.
- **Función `start_scheduler()`**:
  - Usa `schedule` para ejecutar `job_func` cada `interval_minutes`.
  - Ejecuta inmediatamente al arrancar (`run_immediately=True`).
  - Loop infinito con `time.sleep(1)` hasta que el usuario presione `Ctrl+C`.
  - Maneja `KeyboardInterrupt` de forma limpia.

### `src/main.py`

- **Responsabilidad**: Punto de entrada de la aplicación.
- **Flujo**:
  1. Detecta si se pasó `--once` para ejecución única.
  2. Llama a `load_config()` para obtener configuración.
  3. Llama a `setup_logging()` para activar logs.
  4. Crea el `sender` mediante `create_sender()`.
  5. Define `job()` como closure que ejecuta `run_monitoring_cycle()`.
  6. Si `--once`, ejecuta una vez y termina.
  7. Si no, llama a `start_scheduler()` para ejecución continua.

---

## Ejecución

### Modo continuo (producción)

```bash
# Desde la carpeta src
python main.py
```

Salida esperada en consola/logs:

```
2024-06-17 09:00:00 | INFO     | main | ============================================
2024-06-17 09:00:00 | INFO     | main | Iniciando aplicación de monitoreo SQL Server
2024-06-17 09:00:00 | INFO     | main | Base de datos: tenebrosa
2024-06-17 09:00:00 | INFO     | main | Proveedor WhatsApp: whatsapp_business_api
2024-06-17 09:00:00 | INFO     | main | Intervalo: 30 minutos
2024-06-17 09:00:00 | INFO     | main | ============================================
2024-06-17 09:00:01 | INFO     | scheduler | Configurando scheduler cada 30 minutos
2024-06-17 09:00:01 | INFO     | scheduler | Ejecutando ciclo inicial de monitoreo...
2024-06-17 09:00:02 | INFO     | database | Conectando a SQL Server: localhost/tenebrosa
2024-06-17 09:00:02 | INFO     | database | Conexión a SQL Server establecida correctamente.
2024-06-17 09:00:03 | INFO     | monitor | Métricas obtenidas: 15 tablas, 124350 registros
2024-06-17 09:00:04 | INFO     | whatsapp | Enviando mensaje vía WhatsApp Business API a 5215512345678
2024-06-17 09:00:05 | INFO     | whatsapp | Mensaje enviado exitosamente. ID: wamid.XXX
2024-06-17 09:00:05 | INFO     | monitor | Mensaje de WhatsApp enviado correctamente.
2024-06-17 09:00:05 | INFO     | database | Registro de auditoría insertado correctamente.
2024-06-17 09:00:05 | INFO     | monitor | Auditoría registrada en SQL Server.
2024-06-17 09:00:05 | INFO     | scheduler | Scheduler iniciado. Presiona Ctrl+C para detener.
```

### Modo de prueba (una sola ejecución)

```bash
python main.py --once
```

### Ejecutar como servicio en Windows

Opción A: Usar **Task Scheduler** (Programador de Tareas)
1. Crear tarea básica.
2. Activar: "Al iniciar la sesión" o "Diariamente".
3. Acción: Iniciar programa.
4. Programa: `C:\MonitoreoDB\venv\Scripts\python.exe`
5. Argumentos: `src/main.py`
6. Carpeta de inicio: `C:\MonitoreoDB`

Opción B: Convertir a servicio con `nssm` o `pywin32`

```bash
pip install pywin32
```

Crear un script de servicio (fuera del alcance básico, pero documentado en `docs/servicio_windows.md` si se requiere).

---

## Resolución de Problemas

### Error: `pyodbc.Error: ('01000', "[01000] ... [Microsoft][ODBC Driver Manager] ...")`

- **Causa**: No está instalado el driver ODBC.
- **Solución**: Instalar *ODBC Driver 17 for SQL Server* o *18*.

### Error: `Login failed for user 'sa'`

- **Causa**: Credenciales incorrectas o modo de autenticación no habilitado.
- **Solución**: Verificar usuario/contraseña en `.env`. Si usas Windows Auth, cambia `DB_TRUSTED_CONNECTION=yes`.

### Error: `WhatsApp API: 400 Bad Request`

- **Causa**: Número de teléfono destino mal formado o no registrado en Meta.
- **Solución**: El número debe incluir código de país sin signos `+` ni espacios (ej: `5215512345678`). Verificar que el número destino haya aceptado los términos de WhatsApp Business API.

### Error: `No module named 'pyodbc'`

- **Causa**: Entorno virtual no activado o dependencias no instaladas.
- **Solución**: `pip install -r requirements.txt` dentro del `venv`.

### Error: `Access Denied` al escribir logs

- **Causa**: La carpeta `logs/` no existe o no tiene permisos.
- **Solución**: La aplicación crea automáticamente la carpeta, pero verifica que el usuario tenga permisos de escritura.

### UZAPI: `Session desconectada` o `No se puede enviar mensaje`

- **Causa**: El teléfono se desconectó de UZAPI o el celular perdió internet.
- **Solución**: Ve a tu panel de UZAPI (`https://teste.uzapi.com.br:3333`) y verifica que diga **"Status: Conectado"**. Si dice "Desconectado", reescanea el QR con WhatsApp.
- **Causa**: La API de UZAPI tiene un endpoint o campos del body ligeramente diferentes según la versión.
- **Solución**: Revisa tu documentación de Postman. Si el endpoint es diferente (ej: `/api/send-message` vs `/api/messages/send`), ajusta `UZAPI_SEND_PATH` en el `.env`. Si el body usa `number` en vez de `phone`, cambia `UZAPI_PHONE_FIELD=number`.

---

## Notas de Seguridad

1. **Nunca versiones el archivo `.env`**. Agregarlo a `.gitignore`:
   ```
   .env
   venv/
   logs/*.log
   __pycache__/
   ```
2. **Token de WhatsApp**: Trata `WHATSAPP_ACCESS_TOKEN` como una contraseña. Rota el token periódicamente.
3. **Contraseña de SQL**: En producción, usa autenticación Windows (`Trusted_Connection=yes`) o almacena credenciales en un vault (Azure Key Vault, AWS Secrets Manager, etc.).
4. **SQL Injection**: El código usa **parametrización** (`cursor.execute(query, params)`) en todas las queries, protegiendo contra inyección SQL.
5. **Logs**: El archivo de log no registra contraseñas ni tokens.

---

## Licencia

Uso interno. Modificar según necesidades de la organización.

---

## Autor

Desarrollado por el equipo de automatización.
