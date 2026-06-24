# Tenebrosa Dashboard

Sistema de monitoreo que consulta SQL Server y envía reportes periódicos de tablas por WhatsApp vía Evolution API. Incluye backend en Flask, frontend en React y servicios Docker para la infraestructura de mensajería.

## Arquitectura

- **Evolution API** (Docker): Servicio de WhatsApp (puerto `8080`).
- **PostgreSQL + Redis** (Docker): Base de datos y cache de Evolution.
- **Backend** (Python/Flask): API REST para consultar SQL Server y disparar mensajes (puerto `5000`).
- **Frontend** (React/Vite): Panel para controlar el envío y ver estado.

## Requisitos

- Docker y Docker Compose
- Python 3.11+
- Node.js 18+
- SQL Server con base de datos `TenebrosaOLTP`
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

## Ejecución

```bash
# 1. Infraestructura (Evolution API + PostgreSQL + Redis)
docker-compose up -d

# 2. Backend
cd dashboard/backend
pip install -r requirements.txt
python app.py

# 3. Frontend (en otra terminal)
cd dashboard/frontend
npm install
npm run dev
```

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
