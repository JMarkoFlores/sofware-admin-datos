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
