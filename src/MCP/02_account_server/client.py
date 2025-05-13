import asyncio

from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio

from .accounts_client import (get_accounts_tools_openai, list_accounts_tools, read_accounts_resource)

# Define the server parameters
params = {"command": "python", "args": ["src/MCP/02_account_server/accounts_server.py"]}


async def list_tools():
    """
    List the tools available on the server.
    """
    async with MCPServerStdio(params=params) as server:
        mcp_tools = await server.list_tools()
        print(f"Available tools: {mcp_tools}\n")
        for tool in mcp_tools:
            print(f"  - {tool.name}: {tool.description}\n")




async def process_query(query: str, instructions: str):
    """
    Process a query on the server.

    Args:
        query (str): The query to process.
        instructions (str): The instructions for the agent.
    """
    async with MCPServerStdio(params=params) as mcp_server:
        agent = Agent(name="account_manager", 
                      instructions=instructions, 
                      model="gpt-4o-mini", 
                      mcp_servers=[mcp_server]
                      )
        with trace("account_manager"):
            result = await Runner.run(agent, query)
        print(result.final_output)


async def client_tools():
    mcp_tools = await list_accounts_tools()
    print("\nMCP Tools: ", mcp_tools, "\n")
    openai_tools = await get_accounts_tools_openai()
    print("OpenAI Tools: ", openai_tools, "\n")
    context = await read_accounts_resource("YC")
    print("Context: ", context, "\n")



async def process_query_with_tools(query: str, instructions: str):
    """
    Process a query with tools.

    Args:
        query (str): The query to process.
        instructions (str): The instructions for the agent.
    """
    openai_tools = await get_accounts_tools_openai()
    agent = Agent(name="account_manager", instructions=instructions, model="gpt-4o-mini", tools=openai_tools)
    result = await Runner.run(agent, query)
    print(result.final_output)




if __name__ == "__main__":
    print("Listing tools...\n")
    asyncio.run(list_tools())

    print("\nProcessing query...")
    instructions = "You are able to manage an account for a client, and answer questions about the account."
    query = "My name is Ed and my account is under the name Ed. What's my balance and my holdings?"
    asyncio.run(process_query(query, instructions))

    print("\nListing tools again...")
    asyncio.run(client_tools())

    print("\nProcessing query with tools...")
    asyncio.run(process_query_with_tools(query, instructions))

