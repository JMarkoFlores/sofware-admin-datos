-- Script de configuración para el monitoreo de seguridad de login en SQL Server
-- Este script crea un usuario de prueba y verifica la configuración del log de errores

-- 1. Crear un usuario de prueba para simular intentos fallidos
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'TestUserSeguridad')
BEGIN
    CREATE LOGIN [TestUserSeguridad] WITH PASSWORD = 'Temp123!Seguridad', CHECK_POLICY = OFF;
    PRINT 'Login TestUserSeguridad creado.';
END
ELSE
BEGIN
    PRINT 'Login TestUserSeguridad ya existe.';
END
GO

-- 2. Verificar que el log de errores esté habilitado (debe estarlo por defecto)
PRINT '';
PRINT '--- Verificación de la configuración del log de errores ---';
EXEC xp_instance_regread N'HKEY_LOCAL_MACHINE', N'Software\Microsoft\MSSQLServer\MSSQLServer', N'AuditLevel';
GO

-- 3. Consultar el log de errores para ver entradas recientes
PRINT '';
PRINT '--- Últimas entradas del log de errores (Login failed) ---';
EXEC xp_readerrorlog 0, 1, 'Login failed', NULL, NULL, NULL, 'DESC';
GO

-- 4. Para probar manualmente: intenta conectarte con TestUserSeguridad usando una contraseña incorrecta
--    y luego ejecuta nuevamente el comando xp_readerrorlog para ver la entrada
GO

-- 5. Consultar logins existentes
PRINT '';
PRINT '--- Logins existentes en el servidor ---';
SELECT name, type_desc, is_disabled, create_date
FROM sys.server_principals
WHERE type IN ('S', 'U')
ORDER BY name;
GO

-- NOTAS:
-- - El usuario de la aplicación Flask necesita permisos para ejecutar xp_readerrorlog.
-- - Si hay problemas de permisos, ejecuta: GRANT EXECUTE ON xp_readerrorlog TO [tu_usuario];
GO

