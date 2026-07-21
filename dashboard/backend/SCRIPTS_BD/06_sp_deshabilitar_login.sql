USE [master];
GO

-- ========================================================
-- Stored Procedure: sp_DeshabilitarLogin
-- Descripcion: Procedimiento seguro para verificar y 
--              deshabilitar un login en SQL Server. Se usa
--              tras detectar intentos fallidos (Error 18456).
-- ========================================================

IF OBJECT_ID('dbo.sp_DeshabilitarLogin', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_DeshabilitarLogin;
GO

CREATE PROCEDURE dbo.sp_DeshabilitarLogin
    @Username NVARCHAR(128)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @SQL NVARCHAR(MAX);

    -- Verificar si el login existe (tipos 'S' para SQL y 'U' para Windows)
    IF EXISTS (
        SELECT 1 
        FROM sys.server_principals 
        WHERE name = @Username AND type IN ('S', 'U')
    )
    BEGIN
        -- Deshabilitar el login usando SQL Dinamico, ya que ALTER LOGIN 
        -- requiere que el nombre del login sea un identificador directo.
        SET @SQL = N'ALTER LOGIN ' + QUOTENAME(@Username) + N' DISABLE;';
        
        BEGIN TRY
            EXEC sp_executesql @SQL;
            SELECT 1 AS Exito, 'Login ' + @Username + ' deshabilitado exitosamente.' AS Mensaje;
        END TRY
        BEGIN CATCH
            SELECT 0 AS Exito, 'Error al deshabilitar el login: ' + ERROR_MESSAGE() AS Mensaje;
        END CATCH
    END
    ELSE
    BEGIN
        SELECT 0 AS Exito, 'El login ' + @Username + ' no existe en el servidor SQL Server.' AS Mensaje;
    END
END;
GO

PRINT 'sp_DeshabilitarLogin creado correctamente en master.';
GO
