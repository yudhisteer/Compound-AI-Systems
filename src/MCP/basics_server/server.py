from mcp.server.fastmcp import FastMCP

"""
This file contains the main server implementation for the HelloWorld MCP server.

It demonstrates how to:
- Create an MCP server
- Add tools
- Add resources with dynamic and static values
- Define prompt templates
- Run the server
"""

# Create an MCP server
mcp = FastMCP(name="Basics",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

#------------------------------------------
# Tools
#------------------------------------------

# Add a simple hello world tool
@mcp.tool()
def hello_world(name: str = "World") -> str:
    """Returns a friendly greeting message"""
    return f"Hello, {name}!"

# Add a tool to calculate the sum of two numbers
@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Returns the sum of two numbers"""
    return a + b



#------------------------------------------
# Resources
#------------------------------------------

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Add a static greeting resource
@mcp.resource("greeting://default")
def get_default_greeting() -> str:
    """Get the default greeting"""
    return "Hello, World!"

#------------------------------------------
# Prompts
#------------------------------------------

# Add a prompt template
@mcp.prompt("get-started")
def get_started_prompt() -> str:
    """A helpful prompt to get started with the HelloWorld server"""
    return """You are using the HelloWorld MCP server. Here are some things you can try:

1. Say hello to the world:
   - Use the hello_world tool without parameters
   - Example: "Say hello to the world"

2. Greet someone specific:
   - Use the hello_world tool with a name
   - Example: "Say hello to Alice"

3. Access the greeting resource:
   - Use the greeting://{name} resource
   - Example: "Get a greeting for Bob"

The server is simple but demonstrates the basic MCP concepts of tools, resources, and prompts."""

if __name__ == "__main__":
    """
    How to run:
    cd src/mcp-servers/basics_server
    mcp dev server.py
    """
    transport = "sse"
    if transport == "stdio":
        print("Running server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")
