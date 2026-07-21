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

    -- Retornar los libros más prestados con información adicional
    SELECT TOP (@top_n)
        l.titulo AS titulo_libro,
        a.nombre AS autor,
        c.nombre AS categoria,
        COUNT(p.id) AS total_prestamos,
        l.ejemplares_disponibles,
        l.ejemplares_total,
        CAST(l.ejemplares_disponibles AS VARCHAR) + '/' + CAST(l.ejemplares_total AS VARCHAR) AS disponibilidad
    FROM libros l
    INNER JOIN prestamos p ON l.id = p.libro_id
    LEFT JOIN autores a ON l.autor_id = a.id
    LEFT JOIN categorias c ON l.categoria_id = c.id
    GROUP BY l.id, l.titulo, a.nombre, c.nombre, l.ejemplares_disponibles, l.ejemplares_total
    ORDER BY total_prestamos DESC;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_libros_mas_prestados @top_n = 5;
