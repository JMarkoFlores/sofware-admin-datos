USE [msdb];
GO

-- ========================================================
-- Stored Procedure: sp_VerificarBackupHoy
-- Descripcion: Verifica si existe un backup del dia actual
--              para una base de datos especifica y valida
--              que el archivo fisico aun exista en disco.
-- ========================================================

IF OBJECT_ID('dbo.sp_VerificarBackupHoy', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_VerificarBackupHoy;
GO

CREATE PROCEDURE dbo.sp_VerificarBackupHoy
    @DatabaseName NVARCHAR(128)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        DECLARE @RutaBackup NVARCHAR(500);
        DECLARE @HoraBackup DATETIME;
        DECLARE @FileExists INT;

        -- Buscar el backup mas reciente del dia actual
        SELECT TOP 1
            @RutaBackup = mf.physical_device_name,
            @HoraBackup = bs.backup_start_date
        FROM msdb.dbo.backupset bs
        JOIN msdb.dbo.backupmediafamily mf ON bs.media_set_id = mf.media_set_id
        WHERE bs.database_name = @DatabaseName
          AND bs.backup_start_date >= CAST(GETDATE() AS DATE)
        ORDER BY bs.backup_start_date DESC;

        IF @RutaBackup IS NULL
        BEGIN
            SELECT
                0 AS Existe,
                NULL AS Ruta,
                NULL AS Hora,
                NULL AS TamanioMB,
                'No se encontro registro de backup de ' + @DatabaseName + ' para el dia de hoy.' AS Mensaje;
            RETURN;
        END

        -- Verificar que el archivo fisico exista
        EXEC master.dbo.xp_fileexist @RutaBackup, @FileExists OUTPUT;

        IF @FileExists <> 1
        BEGIN
            SELECT
                0 AS Existe,
                @RutaBackup AS Ruta,
                NULL AS Hora,
                NULL AS TamanioMB,
                'El registro de backup existe pero el archivo fue eliminado o no se encuentra: ' + @RutaBackup AS Mensaje;
            RETURN;
        END

        SELECT
            1 AS Existe,
            @RutaBackup AS Ruta,
            @HoraBackup AS Hora,
            NULL AS TamanioMB,
            'Backup verificado: ' + @RutaBackup AS Mensaje;

    END TRY
    BEGIN CATCH
        SELECT
            0 AS Existe,
            NULL AS Ruta,
            NULL AS Hora,
            NULL AS TamanioMB,
            'Error al verificar backup: ' + ERROR_MESSAGE() AS Mensaje;
    END CATCH
END;
GO

PRINT 'sp_VerificarBackupHoy creado correctamente en msdb.';
GO
