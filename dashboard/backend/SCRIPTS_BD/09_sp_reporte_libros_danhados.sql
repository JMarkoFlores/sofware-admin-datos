-- ============================================================
-- Script 09: Stored Procedure para Reporte de Libros Dañados
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_reporte_libros_danhados
    @dias INT = 30
AS
BEGIN
    SET NOCOUNT ON;

    -- Validar parámetro
    IF @dias < 1 OR @dias > 365
    BEGIN
        RAISERROR('El parámetro @dias debe estar entre 1 y 365.', 16, 1);
        RETURN;
    END

    -- Calcular fecha límite
    DECLARE @fecha_limite DATETIME;
    SET @fecha_limite = DATEADD(DAY, -@dias, GETDATE());

    -- Retornar libros dañados en los últimos N días
    SELECT 
        l.titulo AS titulo_libro,
        COUNT(d.id) AS total_danios
    FROM libros l
    INNER JOIN prestamos p ON l.id = p.libro_id
    INNER JOIN devoluciones d ON p.id = d.prestamo_id
    WHERE d.estado_libro = 'dañado'
      AND d.created_at >= @fecha_limite
    GROUP BY l.id, l.titulo
    ORDER BY total_danios DESC;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_libros_danhados @dias = 30;
