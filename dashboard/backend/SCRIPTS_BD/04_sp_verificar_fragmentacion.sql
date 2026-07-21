-- ============================================================
-- Script 04: Stored Procedure para Verificación de Fragmentación
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_verificar_fragmentacion
    @umbral INT = 30
AS
BEGIN
    SET NOCOUNT ON;

    -- Validar que el umbral esté en rango válido
    IF @umbral < 1 OR @umbral > 100
    BEGIN
        RAISERROR('El umbral debe estar entre 1 y 100.', 16, 1);
        RETURN;
    END

    -- Retorna los índices cuya fragmentación supera el umbral
    SELECT
        t.name                                          AS tabla,
        i.name                                          AS indice,
        ROUND(ps.avg_fragmentation_in_percent, 2)       AS fragmentacion,
        ps.page_count                                   AS paginas
    FROM sys.dm_db_index_physical_stats(
             DB_ID(), NULL, NULL, NULL, 'LIMITED'
         ) ps
    INNER JOIN sys.tables  t ON ps.object_id = t.object_id
    INNER JOIN sys.indexes i ON ps.object_id = i.object_id
                             AND ps.index_id  = i.index_id
    WHERE ps.index_id > 0            -- excluir HEAPs
      AND ps.page_count > 0          -- excluir índices vacíos
      AND ps.avg_fragmentation_in_percent >= @umbral
    ORDER BY ps.avg_fragmentation_in_percent DESC;
END;
GO
