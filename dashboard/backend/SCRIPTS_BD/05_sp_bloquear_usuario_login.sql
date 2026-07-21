-- =============================================
-- Procedimiento Almacenado: sp_BloquearUsuarioLogin
-- Descripción: Deshabilita un login de SQL Server usando ALTER LOGIN ... DISABLE
-- Parámetros: @LoginName NVARCHAR(100) - Nombre del login a deshabilitar
-- =============================================

USE [master]
GO

IF OBJECT_ID('dbo.sp_BloquearUsuarioLogin', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_BloquearUsuarioLogin
GO

CREATE PROCEDURE dbo.sp_BloquearUsuarioLogin
    @LoginName NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    -- Variable para el comando dinámico
    DECLARE @SQL NVARCHAR(MAX);

    -- Verificar que el login existe
    IF EXISTS (
        SELECT 1 
        FROM sys.server_principals 
        WHERE name = @LoginName AND type IN ('S', 'U')
    )
    BEGIN
        -- Construir el comando ALTER LOGIN con seguridad (QUOTENAME)
        SET @SQL = N'ALTER LOGIN ' + QUOTENAME(@LoginName) + N' DISABLE;';

        -- Ejecutar el comando dinámico
        EXEC sp_executesql @SQL;

        PRINT 'Login ' + QUOTENAME(@LoginName) + ' deshabilitado exitosamente';
    END
    ELSE
    BEGIN
        RAISERROR('El login %s no existe en SQL Server', 16, 1, @LoginName);
    END
END
GO

-- =============================================
-- Ejemplo de uso:
-- EXEC dbo.sp_BloquearUsuarioLogin @LoginName = 'NombreDelLogin';
-- =============================================
