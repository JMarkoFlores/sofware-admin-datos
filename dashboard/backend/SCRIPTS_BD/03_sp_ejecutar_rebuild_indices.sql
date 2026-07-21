-- ============================================================
-- Script 03: Stored Procedure para Rebuild de Índices
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_ejecutar_rebuild_indices
    @fill_factor INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validar que el fill factor esté en rango válido
    IF @fill_factor < 1 OR @fill_factor > 100
    BEGIN
        RAISERROR('El fill factor debe estar entre 1 y 100.', 16, 1);
        RETURN;
    END

    DECLARE @tabla    NVARCHAR(256);
    DECLARE @sql      NVARCHAR(MAX);
    DECLARE @ok_count INT = 0;
    DECLARE @err_count INT = 0;

    -- Cursor sobre las tablas de usuario en el schema dbo
    DECLARE db_cursor CURSOR LOCAL FAST_FORWARD FOR
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
          AND TABLE_SCHEMA = 'dbo'
        ORDER BY TABLE_NAME;

    OPEN db_cursor;
    FETCH NEXT FROM db_cursor INTO @tabla;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        BEGIN TRY
            -- Construir y ejecutar el ALTER INDEX de forma segura
            SET @sql = N'ALTER INDEX ALL ON [dbo].[' + @tabla
                     + N'] REBUILD WITH (FILLFACTOR = '
                     + CAST(@fill_factor AS NVARCHAR(3)) + N');';
            EXEC sp_executesql @sql;
            SET @ok_count += 1;
        END TRY
        BEGIN CATCH
            -- Continuar con la siguiente tabla si hay error
            SET @err_count += 1;
        END CATCH

        FETCH NEXT FROM db_cursor INTO @tabla;
    END;

    CLOSE db_cursor;
    DEALLOCATE db_cursor;

    -- Retornar resumen
    SELECT
        @ok_count  AS tablas_procesadas,
        @err_count AS tablas_con_error,
        @fill_factor AS fill_factor_aplicado;
END;
GO
