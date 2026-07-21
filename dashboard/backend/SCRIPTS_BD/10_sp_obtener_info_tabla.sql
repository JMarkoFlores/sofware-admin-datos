-- Procedimiento almacenado sp10: Obtiene información de las tablas de usuario
-- Base de datos: Bibliouni
-- Autor: Sistema
-- Fecha: 2026-07-21

USE Bibliouni
GO

IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_ObtenerInfoTablas]') AND type in (N'P', N'PC'))
DROP PROCEDURE [dbo].[sp_ObtenerInfoTablas]
GO

CREATE PROCEDURE [dbo].[sp_ObtenerInfoTablas]
AS
BEGIN
    -- Devuelve los nombres de todas las tablas de usuario en el esquema dbo
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE' 
      AND TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME
END
GO
