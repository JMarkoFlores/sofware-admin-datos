1. Docker-compose.yml >> Crear instancia jean en evolution api
2. (venv) C:\Users\jeanm\Downloads\Software-Datos\dashboard\backend>python app.py
3. C:\Users\jeanm\Downloads\Software-Datos\dashboard\frontend>npm run dev

---

RESTORE FILELISTONLY
FROM DISK = N'C:\Temp\BibliouniBackups\Bibliouni_20260625_075625.bak';
GO

---

RESTORE DATABASE [teste]
FROM DISK = N'C:\Temp\BibliouniBackups\Bibliouni_20260625_075625.bak'
WITH FILE = 1,
MOVE N'Bibliouni' TO N'C:\Program Files\Microsoft SQL Server\MSSQL17.MSSQLSERVER\MSSQL\DATA\teste.mdf',
MOVE N'Bibliouni_log' TO N'C:\Program Files\Microsoft SQL Server\MSSQL17.MSSQLSERVER\MSSQL\DATA\teste_log.ldf',
REPLACE,
NOUNLOAD, STATS = 10;
GO
