# Scripts de Base de Datos - Bibliouni Backup

Esta carpeta contiene los Stored Procedures que el backend de Bibliouni utiliza para la gestion de backups.

## Archivos

1. `01_sp_verificar_backup_hoy.sql` - Crea `sp_VerificarBackupHoy` en `msdb`.
2. `02_sp_ejecutar_backup_bibliouni.sql` - Crea `sp_EjecutarBackupBibliouni` en `master`.

## Instrucciones de ejecucion

### 1. sp_VerificarBackupHoy

Abre SQL Server Management Studio (SSMS) y ejecuta el script `01_sp_verificar_backup_hoy.sql`.

Este script crea el Stored Procedure en la base de datos `msdb`, ya que consulta las tablas del historial de backups (`msdb.dbo.backupset` y `msdb.dbo.backupmediafamily`).

### 2. sp_EjecutarBackupBibliouni

Abre SQL Server Management Studio (SSMS) y ejecuta el script `02_sp_ejecutar_backup_bibliouni.sql`.

Este script crea el Stored Procedure en la base de datos `master`, ya que ejecuta el comando `BACKUP DATABASE`.

## Notas importantes

- La ruta de backup es fija: `C:\Temp\BibliouniBackups\`.
- El nombre del archivo generado usa el formato: `Bibliouni_YYYYMMDD_HHMMSS.bak`.
- Asegurate de que la cuenta de Windows que ejecuta el servicio de SQL Server tenga permisos de lectura/escritura en `C:\Temp\BibliouniBackups\`.
- El backend se conecta con autenticacion de Windows (Trusted Connection).

## Firmas de los Stored Procedures

### sp_VerificarBackupHoy

```sql
EXEC msdb.dbo.sp_VerificarBackupHoy @DatabaseName = 'Bibliouni';
```

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `Existe` | `BIT` | 1 si existe backup valido, 0 si no |
| `Ruta` | `NVARCHAR(500)` | Ruta fisica del archivo `.bak` |
| `Hora` | `DATETIME` | Fecha/hora del backup |
| `TamanioMB` | `DECIMAL(10,2)` | Tamano en MB (actualmente NULL) |
| `Mensaje` | `NVARCHAR(500)` | Mensaje descriptivo |

### sp_EjecutarBackupBibliouni

```sql
EXEC master.dbo.sp_EjecutarBackupBibliouni @DatabaseName = 'Bibliouni';
```

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `Exito` | `BIT` | 1 si se ejecuto correctamente |
| `RutaCompleta` | `NVARCHAR(500)` | Ruta completa del `.bak` generado |
| `Mensaje` | `NVARCHAR(500)` | Mensaje descriptivo o error |

## Prueba manual

### Verificar backup del dia

```sql
USE [msdb];
GO

EXEC dbo.sp_VerificarBackupHoy @DatabaseName = 'Bibliouni';
```

### Ejecutar backup

```sql
USE [master];
GO

EXEC dbo.sp_EjecutarBackupBibliouni @DatabaseName = 'Bibliouni';
```

---

## Scripts de Factor de Llenado y Fragmentación

3. `03_sp_ejecutar_rebuild_indices.sql` - Crea `sp_ejecutar_rebuild_indices` en `Bibliouni`.
4. `04_sp_verificar_fragmentacion.sql` - Crea `sp_verificar_fragmentacion` en `Bibliouni`.

### sp_ejecutar_rebuild_indices

Reconstruye los índices de todas las tablas de usuario en `Bibliouni` con el fill factor indicado.

```sql
USE Bibliouni;
GO
EXEC dbo.sp_ejecutar_rebuild_indices @fill_factor = 80;
```

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `tablas_procesadas` | `INT` | Cantidad de tablas procesadas exitosamente |
| `tablas_con_error` | `INT` | Cantidad de tablas que fallaron |
| `fill_factor_aplicado` | `INT` | Fill factor usado en el rebuild |

### sp_verificar_fragmentacion

Retorna los índices de `Bibliouni` cuya fragmentación supera el umbral indicado.

```sql
USE Bibliouni;
GO
EXEC dbo.sp_verificar_fragmentacion @umbral = 30;
```

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `tabla` | `NVARCHAR` | Nombre de la tabla |
| `indice` | `NVARCHAR` | Nombre del índice |
| `fragmentacion` | `DECIMAL` | Porcentaje de fragmentación promedio |
| `paginas` | `BIGINT` | Cantidad de páginas del índice |

---

## Scripts de Reportes

5. `05_sp_reporte_estadisticas_generales.sql` - Crea `sp_reporte_estadisticas_generales` en `Bibliouni`.
6. `06_sp_reporte_libros_mas_prestados.sql` - Crea `sp_reporte_libros_mas_prestados` en `Bibliouni`.
7. `07_sp_reporte_multas_pendientes.sql` - Crea `sp_reporte_multas_pendientes` en `Bibliouni`.
8. `08_sp_reporte_prestamos_vencidos.sql` - Crea `sp_reporte_prestamos_vencidos` en `Bibliouni`.
9. `09_sp_reporte_libros_danhados.sql` - Crea `sp_reporte_libros_danhados` en `Bibliouni`.

### sp_reporte_estadisticas_generales

Retorna estadísticas generales de la biblioteca.

```sql
USE Bibliouni;
GO
EXEC dbo.sp_reporte_estadisticas_generales;
```

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `total_libros` | `INT` | Total de libros (títulos únicos) |
| `total_ejemplares` | `INT` | Total de ejemplares (suma de ejemplares_total) |
| `libros_disponibles` | `INT` | Suma de ejemplares disponibles |
| `porcentaje_disponibles` | `DECIMAL(5,2)` | Porcentaje de ejemplares disponibles |
| `total_autores` | `INT` | Total de autores |
| `total_categorias` | `INT` | Total de categorías |
| `total_lectores` | `INT` | Total de lectores |
| `prestamos_activos` | `INT` | Préstamos en estado activo |
| `promedio_prestamos_lector` | `DECIMAL(5,2)` | Promedio de préstamos por lector |
| `multas_pendientes` | `INT` | Cantidad de multas no pagadas |
| `monto_multas_pendientes` | `DECIMAL(10,2)` | Monto total de multas pendientes |

### sp_reporte_libros_mas_prestados

Retorna los libros más prestados.

```sql
USE Bibliouni;
GO
EXEC dbo.sp_reporte_libros_mas_prestados @top_n = 20;
```

Parámetros:
- `@top_n` (INT, default 20): Cantidad de libros a retornar (1-100)

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `titulo_libro` | `NVARCHAR` | Título del libro |
| `autor` | `NVARCHAR` | Nombre del autor |
| `categoria` | `NVARCHAR` | Categoría del libro |
| `total_prestamos` | `INT` | Cantidad total de préstamos |
| `ejemplares_disponibles` | `INT` | Ejemplares disponibles |
| `ejemplares_total` | `INT` | Total de ejemplares |
| `disponibilidad` | `VARCHAR` | Formato "disponibles/total" |

### sp_reporte_multas_pendientes

Retorna multas pendientes ordenadas por monto.

```sql
USE Bibliouni;
GO
EXEC dbo.sp_reporte_multas_pendientes @top_n = 20;
```

Parámetros:
- `@top_n` (INT, default 20): Cantidad de multas a retornar (1-100)

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `lector` | `NVARCHAR` | Nombre completo del lector |
| `carrera` | `NVARCHAR` | Carrera del lector |
| `monto` | `DECIMAL` | Monto de la multa |
| `motivo` | `NVARCHAR` | Motivo de la multa |
| `fecha_creacion` | `VARCHAR(10)` | Fecha de creación (YYYY-MM-DD) |
| `dias_desde_creacion` | `INT` | Días desde que se generó la multa |

### sp_reporte_prestamos_vencidos

Retorna préstamos vencidos (activos con fecha esperada pasada).

```sql
USE Bibliouni;
GO
EXEC dbo.sp_reporte_prestamos_vencidos @top_n = 20;
```

Parámetros:
- `@top_n` (INT, default 20): Cantidad de préstamos a retornar (1-100)

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `lector` | `NVARCHAR` | Nombre completo del lector |
| `telefono` | `NVARCHAR` | Teléfono del lector |
| `libro` | `NVARCHAR` | Título del libro |
| `vencido_desde` | `VARCHAR(10)` | Fecha de vencimiento (YYYY-MM-DD) |
| `dias_retraso` | `INT` | Días de retraso |

### sp_reporte_libros_danhados

Retorna libros reportados como dañados en los últimos N días.

```sql
USE Bibliouni;
GO
EXEC dbo.sp_reporte_libros_danhados @dias = 30;
```

Parámetros:
- `@dias` (INT, default 30): Días a considerar hacia atrás (1-365)

Devuelve un SELECT con las columnas:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `titulo_libro` | `NVARCHAR` | Título del libro |
| `lector_responsable` | `NVARCHAR` | Nombre del lector responsable |
| `fecha_dano` | `VARCHAR(10)` | Fecha del daño (YYYY-MM-DD) |
| `observaciones` | `NVARCHAR` | Observaciones del daño |
