# MCP para SQL Server

Servidor MCP local que ofrece herramientas de solo lectura para consultar una base de datos SQL Server desde VS Code.

## Requisitos

- Windows
- Python 3.13 (versión usada para validar este proyecto)
- VS Code con soporte para servidores MCP
- Acceso de red a SQL Server y una cuenta SQL con permisos de solo lectura

## Instalación en Windows

1. Clona el repositorio y abre su carpeta en VS Code:

   ```powershell
   git clone <URL_DEL_REPOSITORIO>
   cd MCP-SQL
   code .
   ```

2. Crea y activa un entorno virtual:

   ```powershell
   py -3.13 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, puedes ejecutar los pasos siguientes usando directamente `.\venv\Scripts\python.exe`.

3. Instala las dependencias:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Crea el archivo local `.env` a partir de la plantilla:

   ```powershell
   Copy-Item .env.example .env
   ```

   Completa `.env` únicamente en tu equipo con los datos proporcionados por el administrador de la base de datos:

   ```dotenv
   SQL_SERVER=
   SQL_DATABASE=
   SQL_USER=
   SQL_PASSWORD=
   ```

   No guardes credenciales en el código ni las subas al repositorio. `.env` está excluido por Git.

5. Revisa `.vscode/mcp.json`. Ya contiene la configuración para iniciar el servidor con el entorno virtual del proyecto. Si VS Code no detecta el servidor, abre la paleta de comandos, ejecuta **MCP: List Servers** y selecciona `sqlserver` para iniciarlo.

6. Confirma que las pruebas locales pasan:

   ```powershell
   .\venv\Scripts\python.exe -m unittest -v
   ```

   Estas pruebas usan conexiones simuladas: no necesitan acceso a SQL Server ni modifican datos.

## Uso y verificación

Desde un chat de VS Code con las herramientas MCP habilitadas, verifica que estén disponibles:

- `health_check`: comprueba la conexión e informa el nombre del servidor.
- `listar_tablas`: lista las tablas de usuario.
- `ejecutar_select`: ejecuta una consulta de lectura.

Para una prueba de consulta sencilla, solicita a la herramienta `ejecutar_select`:

```sql
SELECT 1 AS prueba
```

`health_check`, `listar_tablas` y `ejecutar_select` se conectan a la base de datos configurada. La prueba `SELECT 1` no modifica datos. El código de `ejecutar_select` rechaza consultas que no comienzan con `SELECT` o `WITH`, comandos de escritura reconocidos y sentencias múltiples. Por seguridad, configura además `SQL_USER` con permisos de solo lectura en SQL Server.

## Herramientas de consulta

`ejecutar_select` está pensada para consultas `SELECT` de solo lectura. Por ejemplo:

```sql
SELECT TOP 1 *
FROM nombre_de_tabla
ORDER BY columna_fecha DESC
```

No uses esta herramienta para operaciones que cambien datos o el esquema. La validación del servidor no reemplaza los permisos de solo lectura de la cuenta SQL.
