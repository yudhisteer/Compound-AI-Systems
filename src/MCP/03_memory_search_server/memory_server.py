from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
import asyncio

# Initialize the server
params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]}

async def memory_server(query: str):
    """
    Use the memory server to store and retrieve information from conversations.
    
    Args:
        query (str): The user's query or message to process.
        
    Returns:
        str: The agent's response after processing the query with memory context.
    """
    try:
        async with MCPServerStdio(params=params) as memory_server:
            agent = Agent(name="agent", 
                        instructions="You use your entity tools as a persistent memory to store and recall information about your conversations.",
                        model="gpt-4o-mini", 
                        mcp_servers=[memory_server]
                        )
            with trace("conversation"):
                result = await Runner.run(agent, query)
            return result.final_output
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

async def main():
    try:
        # First call
        print("Making first call...")
        result1 = await memory_server("My name is YC. Currently in Seattle. Going to take Boba later in the park. Boba is my cat.")
        print("First call result:", result1)

        # Second call to see if it remembers   
        print("\nMaking second call...")
        result2 = await memory_server("Who is Boba?")
        print("Second call result:", result2)
    except Exception as e:
        print(f"Main error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

