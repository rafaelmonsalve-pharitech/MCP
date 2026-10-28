from mcp.server.fastmcp import FastMCP

from tools.metadata import listar_tablas
from tools.query import ejecutar_select
from tools.monitoring import health_check

mcp = FastMCP("SQLServerAgent")

mcp.tool()(listar_tablas)
mcp.tool()(ejecutar_select)
mcp.tool()(health_check)

if __name__ == "__main__":
    mcp.run(transport="stdio")