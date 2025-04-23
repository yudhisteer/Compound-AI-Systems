from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Optional
from pathlib import Path

# Create an MCP server
mcp = FastMCP("TerminalServer")

@mcp.resource("file://desktop/README.md")
def readme() -> str:
    """Read the contents of README.md from the Desktop directory."""
    desktop_path = Path.home() / "OneDrive - Microsoft" / "Desktop" / "README.md"
    try:
        return desktop_path.read_text()
    except Exception as e:
        return f"Error reading README.md: {str(e)}"

@mcp.tool()
async def terminal(command: str, working_dir: Optional[str] = None) -> str:
    """Execute a terminal command and return its output.
    
    Args:
        command: The command to execute
        working_dir: Optional working directory to execute the command in
        
    Returns:
        str: The command output or error message
    """
    try:
        # Set up the process with optional working directory
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=working_dir
        )
        
        # Get the output and error streams
        stdout, stderr = process.communicate()
        
        # Return combined output or error message
        if process.returncode == 0:
            return stdout.strip() if stdout else "Command executed successfully"
        else:
            return f"Error: {stderr.strip()}"
            
    except Exception as e:
        return f"Error executing command: {str(e)}"


if __name__ == "__main__":
    mcp.run("stdio")
