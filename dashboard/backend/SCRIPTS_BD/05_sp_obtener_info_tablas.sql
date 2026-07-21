USE [Bibliouni];
GO

-- ========================================================
-- Stored Procedure: sp_ObtenerInfoTablas
-- Descripcion: Obtiene la lista de tablas base del esquema dbo
--              para el reporte del Disparador de Mensajes.
-- ========================================================

IF OBJECT_ID('dbo.sp_ObtenerInfoTablas', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_ObtenerInfoTablas;
GO

CREATE PROCEDURE dbo.sp_ObtenerInfoTablas
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE' 
      AND TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME;
END;
GO

PRINT 'sp_ObtenerInfoTablas creado correctamente en Bibliouni.';
GO
