-- =============================================
-- Procedimiento Almacenado: sp_BloquearUsuarioLogin
-- Descripción: Deshabilita un login de SQL Server usando ALTER LOGIN ... DISABLE
-- Parámetros: @LoginName NVARCHAR(100) - Nombre del login a deshabilitar
-- Base de datos: master
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

    DECLARE @SQL NVARCHAR(MAX);
    DECLARE @IsDisabled BIT;

    BEGIN TRY
        -- 1. Validar existencia y obtener estado del login
        SELECT @IsDisabled = is_disabled
        FROM sys.server_principals 
        WHERE name = @LoginName AND type IN ('S', 'U');

        IF @IsDisabled IS NULL
        BEGIN
            RAISERROR('El login ''%s'' no existe en SQL Server', 16, 1, @LoginName);
            RETURN;
        END

        -- 2. Validar si ya está deshabilitado
        IF @IsDisabled = 1
        BEGIN
            PRINT 'El login ' + QUOTENAME(@LoginName) + ' ya se encuentra deshabilitado';
            RETURN;
        END

        -- 3. Protección de cuentas críticas del sistema
        IF LOWER(@LoginName) IN ('sa') OR @LoginName = SUSER_SNAME()
        BEGIN
            RAISERROR('No está permitido deshabilitar la cuenta ''%s'' por seguridad', 16, 1, @LoginName);
            RETURN;
        END

        -- 4. Construir y ejecutar comando dinámico
        SET @SQL = N'ALTER LOGIN ' + QUOTENAME(@LoginName) + N' DISABLE;';
        EXEC sp_executesql @SQL;

        PRINT 'Login ' + QUOTENAME(@LoginName) + ' deshabilitado exitosamente';

    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();

        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END
GO

-- =============================================
-- Ejemplo de uso:
-- EXEC dbo.sp_BloquearUsuarioLogin @LoginName = 'NombreDelLogin';
-- =============================================
