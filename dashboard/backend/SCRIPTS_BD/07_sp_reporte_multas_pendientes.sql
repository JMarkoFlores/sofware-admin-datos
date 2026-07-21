-- ============================================================
-- Script 07: Stored Procedure para Reporte de Multas Pendientes
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_reporte_multas_pendientes
    @top_n INT = 20
AS
BEGIN
    SET NOCOUNT ON;

    -- Validar parámetro
    IF @top_n < 1 OR @top_n > 100
    BEGIN
        RAISERROR('El parámetro @top_n debe estar entre 1 y 100.', 16, 1);
        RETURN;
    END

    -- Retornar multas pendientes ordenadas por monto descendente
    SELECT TOP (@top_n)
        CONCAT(lec.nombres, ' ', lec.apellidos) AS lector,
        m.monto,
        m.motivo
    FROM multas m
    INNER JOIN lectores lec ON m.lector_id = lec.id
    WHERE m.pagada = 0
    ORDER BY m.monto DESC;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_multas_pendientes @top_n = 10;
