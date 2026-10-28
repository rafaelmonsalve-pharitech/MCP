import asyncio

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters
)


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()

            print("\n=== TOOLS ===")

            tools = await session.list_tools()

            for tool in tools.tools:
                print(tool.name)

            print("\n=== HEALTH CHECK ===")

            result = await session.call_tool(
                "health_check",
                {}
            )

            print(result)

            print("\n=== TABLAS ===")

            result = await session.call_tool(
                "listar_tablas",
                {}
            )

            print(result)


if __name__ == "__main__":
    asyncio.run(main())