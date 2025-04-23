import os
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from datetime import datetime
import asyncio

# Set the Brave API key
env = {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}

# Parameters for the server
params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": env}

# Search server
async def search_server(query: str):
    """
    Search the web for information and briefly summarize the takeaways.

    Args:
        query (str): The query to search the web for.

    Returns:
        str: A brief summary of the takeaways from the search.
    """
    async with MCPServerStdio(params=params) as mcp_server:
        agent = Agent(name="agent", instructions = "You are able to search the web for information and briefly summarize the takeaways.", model="gpt-4o-mini", mcp_servers=[mcp_server])
        with trace("conversation"):
            result = await Runner.run(agent, query)
        return result.final_output
    
if __name__ == "__main__":
    try:
        query = f"Please research the latest news on Amazon stock price and briefly summarize its outlook. \
        For context, the current date is {datetime.now().strftime('%Y-%m-%d')}"

        result = asyncio.run(search_server(query))
        print(result)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"An error occurred: {e}")