import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use SSE transport.
3. The server is listening on port 8050.

To run the server:
cd src/MCP/basics_server
change transport = "sse" in server.py
uv run server.py
"""


async def main():
    # Connect to the server using SSE
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool(name="calculate_sum", arguments={"a": 2, "b": 3})
            print(f"Result for 2 + 3 = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())