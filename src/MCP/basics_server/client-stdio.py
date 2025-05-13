import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.shared.utils import debug_print

async def main():
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["src/MCP/basics_server/server.py"],  # Arguments to the command
    )

    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            debug_print(f"Available tools: {tools_result}\n")
            for tool in tools_result.tools:
                debug_print(f"  - {tool.name}: {tool.description}\n")

            # Call our calculator tool
            result = await session.call_tool(name="calculate_sum", arguments={"a": 2, "b": 3})
            print(f"Result for 2 + 3 = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())