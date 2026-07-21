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

    -- Retornar libros dañados con información detallada
    SELECT 
        l.titulo AS titulo_libro,
        CONCAT(lec.nombres, ' ', lec.apellidos) AS lector_responsable,
        CONVERT(VARCHAR(10), d.created_at, 120) AS fecha_dano,
        d.observaciones
    FROM libros l
    INNER JOIN prestamos p ON l.id = p.libro_id
    INNER JOIN devoluciones d ON p.id = d.prestamo_id
    INNER JOIN lectores lec ON p.lector_id = lec.id
    WHERE d.estado_libro = 'dañado'
      AND d.created_at >= @fecha_limite
    ORDER BY d.created_at DESC;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_libros_danhados @dias = 30;
