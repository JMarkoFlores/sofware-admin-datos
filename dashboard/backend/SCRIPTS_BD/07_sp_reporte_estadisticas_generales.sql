-- ============================================================
-- Script 05: Stored Procedure para Reporte de Estadísticas Generales
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_reporte_estadisticas_generales
AS
BEGIN
    SET NOCOUNT ON;

    -- Total de libros (títulos únicos)
    DECLARE @total_libros INT;
    SELECT @total_libros = COUNT(*) FROM libros;

    -- Total de ejemplares (suma de ejemplares_total)
    DECLARE @total_ejemplares INT;
    SELECT @total_ejemplares = ISNULL(SUM(ejemplares_total), 0) FROM libros;

    -- Libros disponibles (suma de ejemplares_disponibles)
    DECLARE @libros_disponibles INT;
    SELECT @libros_disponibles = ISNULL(SUM(ejemplares_disponibles), 0) FROM libros;

    -- Porcentaje de libros disponibles
    DECLARE @porcentaje_disponibles DECIMAL(5, 2);
    IF @total_ejemplares > 0
        SET @porcentaje_disponibles = (@libros_disponibles * 100.0 / @total_ejemplares);
    ELSE
        SET @porcentaje_disponibles = 0;

    -- Total de autores
    DECLARE @total_autores INT;
    SELECT @total_autores = COUNT(*) FROM autores;

    -- Total de categorías
    DECLARE @total_categorias INT;
    SELECT @total_categorias = COUNT(*) FROM categorias;

    -- Total de lectores
    DECLARE @total_lectores INT;
    SELECT @total_lectores = COUNT(*) FROM lectores;

    -- Préstamos activos
    DECLARE @prestamos_activos INT;
    SELECT @prestamos_activos = COUNT(*) FROM prestamos WHERE estado = 'activo';

    -- Promedio de préstamos por lector
    DECLARE @promedio_prestamos_lector DECIMAL(5, 2);
    IF @total_lectores > 0
        SET @promedio_prestamos_lector = CAST(@prestamos_activos AS DECIMAL) / @total_lectores;
    ELSE
        SET @promedio_prestamos_lector = 0;

    -- Multas pendientes (cantidad y monto total)
    DECLARE @multas_pendientes INT;
    DECLARE @monto_multas_pendientes DECIMAL(10, 2);
    
    SELECT 
        @multas_pendientes = COUNT(*),
        @monto_multas_pendientes = ISNULL(SUM(monto), 0)
    FROM multas 
    WHERE pagada = 0;

    -- Retornar resultados como un conjunto de filas
    SELECT 
        @total_libros AS total_libros,
        @total_ejemplares AS total_ejemplares,
        @libros_disponibles AS libros_disponibles,
        @porcentaje_disponibles AS porcentaje_disponibles,
        @total_autores AS total_autores,
        @total_categorias AS total_categorias,
        @total_lectores AS total_lectores,
        @prestamos_activos AS prestamos_activos,
        @promedio_prestamos_lector AS promedio_prestamos_lector,
        @multas_pendientes AS multas_pendientes,
        @monto_multas_pendientes AS monto_multas_pendientes;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_estadisticas_generales;
