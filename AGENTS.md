# AGENTS.md — Sistema Web para la Gestión Operativa de Biblioteca Universitaria

## 1. Nombre del Proyecto
Sistema Web para la Gestión Operativa de Biblioteca Universitaria con Monitoreo de Base de Datos y Notificaciones por WhatsApp.

## 2. Tecnologías Principales
- **Backend:** Python 3.11+, Flask, Flask-SQLAlchemy, Flask-CORS, APScheduler, pyodbc, requests
- **Frontend:** React 18 + Vite, Axios, React Icons
- **Base de datos bibliotecaria:** SQL Server (base de datos `Bibliouni`) — accedida vía SQLAlchemy ORM
- **Base de datos del disparador:** SQL Server (base de datos `TenebrosaOLTP`) — accedida vía pyodbc directo (NO CAMBIAR)
- **WhatsApp / Monitoreo:** Evolution API (Docker: PostgreSQL + Redis + evolution-api)

## 3. Arquitectura del Backend (Flask)
El backend está distribuido en carpetas siguiendo una arquitectura por capas:

```
dashboard/backend/
├── app.py                 # Entry point. Registra blueprints e inicia la app.
├── config/
│   └── settings.py        # Configuraciones centralizadas (.env)
├── models/
│   ├── base.py            # SQLAlchemy Base + engine para Bibliouni
│   ├── autor.py
│   ├── categoria.py
│   ├── libro.py
│   ├── lector.py
│   ├── prestamo.py
│   ├── devolucion.py
│   ├── multa.py
│   ├── usuario_sistema.py
│   └── auditoria.py
├── routes/
│   ├── libros.py          # Blueprint: /api/libros
│   ├── autores.py         # Blueprint: /api/autores
│   ├── categorias.py      # Blueprint: /api/categorias
│   ├── lectores.py        # Blueprint: /api/lectores
│   ├── prestamos.py       # Blueprint: /api/prestamos
│   ├── devoluciones.py    # Blueprint: /api/devoluciones
│   ├── multas.py          # Blueprint: /api/multas
│   ├── usuarios_sistema.py# Blueprint: /api/usuarios
│   ├── reportes.py        # Blueprint: /api/reportes
│   ├── auditoria.py       # Blueprint: /api/auditoria
│   ├── dashboard.py       # Blueprint: /api/dashboard
│   └── disparador.py      # Blueprint: /api/* (preservado intacto)
├── services/
│   ├── libro_service.py
│   ├── prestamo_service.py
│   ├── reporte_service.py
│   └── backup_service.py  # Verificación y ejecución de backups Bibliouni
├── repositories/          # Consultas complejas / raw SQL cuando se requiera
├── database/
│   ├── init_db.py         # Crea tablas de Bibliouni con SQLAlchemy
│   └── seeders/
│       └── seed_all.py    # Inserta 10 registros de prueba por tabla
├── utils/                 # Helpers, validadores, formateadores
├── db_tenebrosa.py        # Conexión pyodbc a TenebrosaOLTP (solo para Disparador)
├── whatsapp.py            # Módulo de envío WhatsApp via Evolution API (intacto)
└── requirements.txt
```

## 4. Reglas Críticas
1. El módulo **Disparador** incluye dos submódulos independientes:
   - **Disparador de Mensajes:** monitorea la base de datos **Bibliouni** vía `db_tenebrosa.py` + `whatsapp.py`. Envia reportes periódicos por WhatsApp con información de tablas y registros.
   - **Disparador de Backup:** verifica diariamente a las 7:00 AM (America/Lima) si existe un backup de Bibliouni. Si no existe, envía alerta por WhatsApp y permite ejecutar el backup remotamente respondiendo `RESUELVE BACKUP`.
2. **NO MODIFICAR** `docker-compose.yml` (PostgreSQL, Redis, Evolution API deben quedar igual).
3. Todos los demás módulos se conectan a la base de datos `Bibliouni` en SQL Server usando SQLAlchemy ORM.
4. Si se necesita agregar un campo o tabla nueva, actualizar: modelo → migración (si aplica) → seeder → service → route → frontend.

## 5. Auditoría Automática
Todas las operaciones **CREATE, UPDATE y DELETE** en los módulos bibliotecarios se registran automáticamente en la tabla `auditoria` mediante la función `log_auditoria()` ubicada en `utils/helpers.py`. Los blueprints de cada módulo llaman a esta función después de cada `db.session.commit()` exitoso. No es necesario agregar logging manual; si se crea un nuevo blueprint, integrar `log_auditoria` siguiendo el patrón existente.

## 6. Base de Datos Bibliouni (SQL Server)
### Tablas
1. **autores** — id, nombre, apellido, nacionalidad, fecha_nacimiento, biografia, created_at
2. **categorias** — id, nombre, descripcion, created_at
3. **libros** — id, titulo, isbn, anio_publicacion, editorial, ejemplares_total, ejemplares_disponibles, autor_id (FK), categoria_id (FK), created_at
4. **lectores** — id, codigo_estudiante, nombres, apellidos, email, telefono, carrera, facultad, activo, created_at
5. **prestamos** — id, lector_id (FK), libro_id (FK), fecha_prestamo, fecha_devolucion_esperada, fecha_devolucion_real, estado (activo/devuelto/vencido), observaciones, created_at
6. **devoluciones** — id, prestamo_id (FK), fecha_devolucion, estado_libro (bueno/dañado/perdido), observaciones, created_at
7. **multas** — id, lector_id (FK), prestamo_id (FK), monto, motivo, pagada (bit), fecha_pago, created_at
8. **usuarios_sistema** — id, username, password_hash, nombre_completo, rol (admin/bibliotecario), activo, ultimo_acceso, created_at
9. **auditoria** — id, tipo_operacion, modulo, descripcion, usuario, resultado, fecha_hora, detalle

### Inicialización
Para crear las tablas y datos de prueba (primera vez):
```bash
cd dashboard/backend
python database/init_db.py
python database/seeders/seed_all.py
```

## 7. Endpoints API
- `/api/health` — Estado general
- `/api/dashboard` — Resumen de métricas
- `/api/libros` — CRUD Libros
- `/api/autores` — CRUD Autores
- `/api/categorias` — CRUD Categorías
- `/api/lectores` — CRUD Lectores
- `/api/prestamos` — Gestión Préstamos
- `/api/devoluciones` — Gestión Devoluciones
- `/api/multas` — Gestión Multas
- `/api/usuarios` — CRUD Usuarios del Sistema
- `/api/reportes/*` — Reportes varios
- `/api/auditoria` — Historial de auditoría
- `/api/start`, `/api/stop`, `/api/status`, `/api/tables`, `/api/test-send` — Disparador WhatsApp (INTACTO)
- `/api/backup/start`, `/api/backup/stop`, `/api/backup/status` — Monitoreo de Backup
- `/api/backup/webhook` — Webhook para comandos entrantes de WhatsApp (`RESUELVE BACKUP`)

## 8. Variables de Entorno (.env)
Ver `dashboard/backend/.env` y `.env.example`:
- `BIBLIOUNI_SERVER`, `BIBLIOUNI_DB`, `BIBLIOUNI_DRIVER`, `BIBLIOUNI_TRUSTED_CONNECTION` — Conexión a Bibliouni
- `DB_SERVER`, `DB_NAME`, `DB_DRIVER`, `DB_TRUSTED_CONNECTION` — Conexión a TenebrosaOLTP (Disparador)
- `EVOLUTION_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE`, `WHATSAPP_DESTINATION` — Evolution API
- `BACKUP_PATH`, `BACKUP_CHECK_HOUR`, `BACKUP_CHECK_MINUTE`, `BACKUP_TIMEZONE`, `WEBHOOK_URL` — Monitoreo de Backup

## 9. Frontend
```
dashboard/frontend/src/
├── components/
│   ├── Sidebar.jsx
│   ├── Dashboard.jsx
│   ├── Libros.jsx
│   ├── Autores.jsx
│   ├── Categorias.jsx
│   ├── Lectores.jsx
│   ├── Prestamos.jsx
│   ├── Devoluciones.jsx
│   ├── Multas.jsx
│   ├── UsuariosSistema.jsx
│   ├── Reportes.jsx
│   ├── Auditoria.jsx
│   └── Disparador.jsx      # Disparador de Mensajes + Disparador de Backup
├── App.jsx
└── styles.css
```

## 10. Instrucciones de Ejecución
1. Asegurar que Docker está corriendo (Evolution API): `docker-compose up -d`
2. Activar entorno virtual Python.
3. Inicializar base de datos: `python database/init_db.py` y `python database/seeders/seed_all.py`
4. Backend: `python app.py` (puerto 5000)
5. Frontend: `npm run dev` (puerto 5173)
