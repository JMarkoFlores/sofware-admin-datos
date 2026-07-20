USE [master];
GO

-- ========================================================
-- Stored Procedure: sp_EjecutarBackupBibliouni
-- Descripcion: Ejecuta un backup FULL de una base de datos
--              a una ruta fija con nombre automatico.
-- ========================================================

IF OBJECT_ID('dbo.sp_EjecutarBackupBibliouni', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_EjecutarBackupBibliouni;
GO

CREATE PROCEDURE dbo.sp_EjecutarBackupBibliouni
    @DatabaseName NVARCHAR(128)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        DECLARE @BackupPath NVARCHAR(500) = 'C:\Temp\BibliouniBackups\';
        DECLARE @NombreArchivo NVARCHAR(128);
        DECLARE @SQL NVARCHAR(MAX);
        DECLARE @DirExists INT;
        DECLARE @Resultado INT;
        DECLARE @RutaCompleta NVARCHAR(500);
        DECLARE @FileExists INT;

        -- Validar que se especifico una base de datos
        IF @DatabaseName IS NULL OR LTRIM(RTRIM(@DatabaseName)) = ''
        BEGIN
            SELECT 0 AS Exito, NULL AS RutaCompleta, 'Debe especificar el nombre de la base de datos.' AS Mensaje;
            RETURN;
        END

        -- Validar que la base de datos existe
        IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = @DatabaseName)
        BEGIN
            SELECT 0 AS Exito, NULL AS RutaCompleta, 'La base de datos especificada no existe: ' + @DatabaseName AS Mensaje;
            RETURN;
        END

        -- Crear la carpeta de backups si no existe
        EXEC master.dbo.xp_fileexist @BackupPath, @DirExists OUTPUT;
        IF @DirExists <> 2 -- 2 = es directorio
        BEGIN
            EXEC @Resultado = master.dbo.xp_create_subdir @BackupPath;
            IF @Resultado <> 0
            BEGIN
                SELECT 0 AS Exito, NULL AS RutaCompleta, 'No se pudo crear la carpeta de backups: ' + @BackupPath AS Mensaje;
                RETURN;
            END
        END

        -- Generar nombre de archivo con fecha y hora
        SET @NombreArchivo = @DatabaseName + '_' + FORMAT(GETDATE(), 'yyyyMMdd_HHmmss') + '.bak';
        SET @RutaCompleta = @BackupPath + @NombreArchivo;

        -- Ejecutar el backup
        SET @SQL = N'BACKUP DATABASE [' + @DatabaseName + N'] ' +
                   N'TO DISK = N''' + @RutaCompleta + N''' ' +
                   N'WITH FORMAT, COMPRESSION, STATS=10;';

        EXEC sp_executesql @SQL;

        -- Verificar que el archivo se creo
        EXEC master.dbo.xp_fileexist @RutaCompleta, @FileExists OUTPUT;
        IF @FileExists <> 1
        BEGIN
            SELECT 0 AS Exito, @RutaCompleta AS RutaCompleta, 'El backup se ejecuto pero el archivo no fue encontrado: ' + @RutaCompleta AS Mensaje;
            RETURN;
        END

        SELECT 1 AS Exito, @RutaCompleta AS RutaCompleta, 'Backup generado exitosamente: ' + @NombreArchivo AS Mensaje;

    END TRY
    BEGIN CATCH
        SELECT 0 AS Exito, NULL AS RutaCompleta, 'Error al generar backup: ' + ERROR_MESSAGE() AS Mensaje;
    END CATCH
END;
GO

PRINT 'sp_EjecutarBackupBibliouni creado correctamente en master.';
GO
