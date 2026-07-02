# Tenebrosa Dashboard

Sistema de monitoreo que consulta SQL Server y envía reportes periódicos de tablas por WhatsApp vía Evolution API. Incluye backend en Flask, frontend en React y servicios Docker para la infraestructura de mensajería.

## ✨ Características Nuevas: Reportes Interactivos por WhatsApp

### 🎯 Flujos Implementados

#### 1. Reportes Automáticos Diarios y Semanales
- 📅 Reportes programados a horas configurables
- 📊 5 tipos diferentes de reportes (estadísticas, multas, libros, etc.)
- 🔔 Envío automático por WhatsApp en horarios definidos
- ⚙️ Totalmente personalizable via `.env`

#### 2. Reportes Interactivos Bajo Demanda
- 💬 Menús dinámicos sin comandos predefinidos
- 🔄 Conversaciones persistentes por usuario
- 📝 Usuario selecciona tipo de reporte (1-5)
- 🔁 Opción de generar otro reporte o cancelar
- ⏱️ Sesiones con timeout configurable

#### 3. Gestión Centralizada desde Panel
- 🎛️ Botón para iniciar/detener reportes automáticos
- 📱 Ingreso de número de WhatsApp editable
- 🧪 Botones de prueba para validar configuración
- 📈 Visualización de próximos reportes programados

### 📊 Tipos de Reportes

| # | Nombre | Descripción |
|---|--------|-------------|
| 1 | 📊 Estadísticas Generales | Total libros, autores, categorías, lectores, préstamos, multas |
| 2 | 📚 Libros Más Prestados | Top 5 de libros más solicitados |
| 3 | 💰 Multas Pendientes | Cantidad y monto total |
| 4 | ⏰ Préstamos Vencidos | Últimos 10 préstamos con retraso |
| 5 | 🔴 Libros Dañados | Reportes de daño (últimos 30 días) |

### 🚀 Inicio Rápido

Ver: **[QUICKSTART_REPORTES.md](QUICKSTART_REPORTES.md)**

Resumen:
1. `python database/init_db.py` - Crear tablas
2. `python app.py` - Iniciar backend
3. `npm run dev` - Iniciar frontend
4. Ir a Disparador → Reportes Automáticos
5. Ingresar número de WhatsApp e "Iniciar Reportes"

### 📚 Documentación Completa

- **[QUICKSTART_REPORTES.md](QUICKSTART_REPORTES.md)** - Guía de inicio rápido
- **[REPORTES_INTERACTIVOS.md](REPORTES_INTERACTIVOS.md)** - Documentación completa
- **[IMPLEMENTACION_REPORTES.txt](IMPLEMENTACION_REPORTES.txt)** - Resumen técnico de cambios

## Arquitectura

- **Evolution API** (Docker): Servicio de WhatsApp (puerto `8080`).
- **PostgreSQL + Redis** (Docker): Base de datos y cache de Evolution.
- **Backend** (Python/Flask): API REST para consultar SQL Server y disparar mensajes (puerto `5000`).
- **Frontend** (React/Vite): Panel para controlar el envío y ver estado.

## Requisitos

- Docker y Docker Compose
- Python 3.11+
- Node.js 18+
- SQL Server con base de datos `TenebrosaOLTP` y `Bibliouni`
- ODBC Driver 17 para SQL Server

## Configuración

1. Copiar y completar variables de entorno:
   ```bash
   cp .env.example .env
   cp dashboard/backend/.env.example dashboard/backend/.env
   ```

2. Ajustar en `.env` (raíz): credenciales de PostgreSQL y Redis para Evolution API.

3. Ajustar en `dashboard/backend/.env`:
   - Conexión a SQL Server (`DB_SERVER`, `DB_NAME`, etc.)
   - URL y API Key de Evolution API (`EVOLUTION_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE`)
   - Número de destino por defecto (`WHATSAPP_DESTINATION`)
   - **Nuevo:** Configuración de reportes automáticos (ver abajo)

## Configuración de Reportes Automáticos

Agregar a `dashboard/backend/.env`:

```env
# Reportes Diarios
REPORTS_DAILY_HOUR=8
REPORTS_DAILY_MINUTE=0
REPORTS_DAILY_TYPES=estadisticas,multas

# Reportes Semanales
REPORTS_WEEKLY_DAY=MON
REPORTS_WEEKLY_HOUR=9
REPORTS_WEEKLY_MINUTE=0
REPORTS_WEEKLY_TYPES=estadisticas,libros_prestados,devoluciones_pendientes

# Zona Horaria
REPORTS_TIMEZONE=America/Lima
```

## Ejecución

```bash
# 1. Infraestructura (Evolution API + PostgreSQL + Redis)
docker-compose up -d

# 2. Inicializar base de datos (crea tabla user_conversations)
cd dashboard/backend
python database/init_db.py

# 3. Backend
python app.py

# 4. Frontend (en otra terminal)
cd dashboard/frontend
npm install
npm run dev
```

## 📁 Archivos Nuevos/Modificados

### Nuevos
- `models/user_conversation.py` - Modelo para persistencia de conversaciones
- `services/interactive_reports_service.py` - Lógica de menús interactivos
- `REPORTES_INTERACTIVOS.md` - Documentación de reportes
- `QUICKSTART_REPORTES.md` - Guía de inicio rápido

### Modificados
- `services/reporte_service.py` - +5 tipos de reportes
- `routes/disparador.py` - +5 endpoints de reportes
- `frontend/src/components/Disparador.jsx` - Nueva sección de reportes
- `dashboard/backend/.env` - Variables de reportes

## Uso

1. Acceder al frontend (por defecto `http://localhost:5173`).
2. Ir al módulo **Disparador**.
3. Ingresar el número de teléfono destino (ej: `51952310138`).
4. Click en **Iniciar**. El sistema enviará inmediatamente un mensaje y luego cada 1 minuto con:
   - Total de tablas en `TenebrosaOLTP`.
   - Lista de nombres de las tablas.

## Endpoints principales (Backend)

| Método | Endpoint        | Descripción                    |
|--------|-----------------|--------------------------------|
| GET    | `/api/health`   | Estado del servicio            |
| GET    | `/api/status`   | Estado del disparador          |
| POST   | `/api/start`    | Iniciar envío programado       |
| GET    | `/api/stop`     | Detener envío programado       |
| GET    | `/api/tables`   | Consultar tablas sin enviar    |
| GET    | `/api/test-send`| Enviar mensaje de prueba       |

## Dependencias principales

- **Backend:** Flask, Flask-CORS, APScheduler, pyodbc, requests, python-dotenv.
- **Frontend:** React, Axios, Vite.
- **Infraestructura:** PostgreSQL 15, Redis 7, Evolution API.
