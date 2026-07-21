-- ============================================================
-- Script 08: Stored Procedure para Reporte de Préstamos Vencidos
-- Base de datos: Bibliouni
-- Ejecutar en: SQL Server Management Studio (SSMS)
-- ============================================================

USE Bibliouni;
GO

CREATE OR ALTER PROCEDURE dbo.sp_reporte_prestamos_vencidos
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

    -- Retornar préstamos vencidos con información adicional
    SELECT TOP (@top_n)
        CONCAT(lec.nombres, ' ', lec.apellidos) AS lector,
        lec.telefono,
        l.titulo AS libro,
        CONVERT(VARCHAR(10), p.fecha_devolucion_esperada, 120) AS vencido_desde,
        DATEDIFF(DAY, p.fecha_devolucion_esperada, GETDATE()) AS dias_retraso
    FROM prestamos p
    INNER JOIN lectores lec ON p.lector_id = lec.id
    INNER JOIN libros l ON p.libro_id = l.id
    WHERE p.estado = 'activo'
      AND p.fecha_devolucion_esperada < CAST(GETDATE() AS DATE)
    ORDER BY p.fecha_devolucion_esperada DESC;
END
GO

-- Prueba del SP
-- EXEC Bibliouni.dbo.sp_reporte_prestamos_vencidos @top_n = 10;
