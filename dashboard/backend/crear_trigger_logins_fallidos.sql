-- Script para crear un LOGON TRIGGER en SQL Server que registra intentos fallidos
-- de inicio de sesión en la tabla AuditoriaLoginsFallidos (que el servicio creará automáticamente)
--
-- IMPORTANTE:
-- 1. Debes ejecutar este script con permisos de sysadmin en SQL Server
-- 2. Si ya existe el trigger, primero lo eliminamos
-- 3. Esto registrará TODOS los intentos fallidos (Error 18456)
--

USE master;
GO

-- Primero, creamos la tabla en master si no existe (por si el servicio no la ha creado aún)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuditoriaLoginsFallidos')
BEGIN
    CREATE TABLE master.dbo.AuditoriaLoginsFallidos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(128) NOT NULL,
        fecha_hora DATETIME DEFAULT GETDATE(),
        ip NVARCHAR(50),
        mensaje NVARCHAR(MAX)
    );
    PRINT '✅ Tabla AuditoriaLoginsFallidos creada en master';
END
ELSE
BEGIN
    PRINT 'ℹ️ Tabla AuditoriaLoginsFallidos ya existe en master';
END
GO

-- Eliminamos el trigger si ya existe para evitar errores
IF EXISTS (SELECT * FROM sys.server_triggers WHERE name = 'AuditarLoginsFallidos')
BEGIN
    DROP TRIGGER AuditarLoginsFallidos ON ALL SERVER;
    PRINT 'ℹ️ Trigger anterior eliminado';
END
GO

-- Ahora creamos el LOGON TRIGGER
CREATE TRIGGER AuditarLoginsFallidos
ON ALL SERVER
FOR LOGON
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @username NVARCHAR(128);
    DECLARE @ip NVARCHAR(50);
    DECLARE @error_number INT;
    DECLARE @error_message NVARCHAR(MAX);

    -- Obtenemos el nombre del usuario que está intentando iniciar sesión
    SET @username = ORIGINAL_LOGIN();
    
    -- Obtenemos la IP del cliente (si está disponible)
    SELECT @ip = client_net_address
    FROM sys.dm_exec_connections
    WHERE session_id = @@SPID;

    -- Obtenemos el último error (si hubo uno)
    SET @error_number = ERROR_NUMBER();
    SET @error_message = ERROR_MESSAGE();

    -- Si el error es 18456 (Login failed for user)
    IF @error_number = 18456
    BEGIN
        BEGIN TRY
            -- Insertamos el registro en la tabla de auditoría
            INSERT INTO master.dbo.AuditoriaLoginsFallidos (username, ip, mensaje)
            VALUES (@username, @ip, @error_message);
        END TRY
        BEGIN CATCH
            -- Si hay error al insertar, no hacemos nada para evitar interrumpir el sistema
            PRINT 'Error al registrar intento fallido en auditoría';
        END CATCH
    END
END
GO

PRINT '✅ Trigger AuditarLoginsFallidos creado exitosamente!';
PRINT 'ℹ️ Este trigger registrará automáticamente todos los intentos fallidos de inicio de sesión en la tabla AuditoriaLoginsFallidos';
GO

-- Para probar que funcione, intenta iniciar sesión con credenciales incorrectas y luego ejecuta:
-- SELECT * FROM master.dbo.AuditoriaLoginsFallidos;

