-- ============================================================
-- Script 06: Stored Procedure para Reporte de Libros Más Prestados
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_reporte_libros_mas_prestados
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

    -- Retornar los libros más prestados
    SELECT TOP (@top_n)
        l.titulo AS titulo_libro,
        COUNT(p.id) AS total_prestamos
    FROM libros l
    INNER JOIN prestamos p ON l.id = p.libro_id
    GROUP BY l.id, l.titulo
    ORDER BY total_prestamos DESC;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_libros_mas_prestados @top_n = 5;
