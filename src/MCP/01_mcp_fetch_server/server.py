from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
import os
import asyncio

load_dotenv()
puppeteer_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-puppeteer"]}

async def main():
    async with MCPServerStdio(params=puppeteer_params) as server:
        puppeteer_tools = await server.list_tools()

    for tool in puppeteer_tools:
        print(f"{tool.name}: {tool.description.replace('\n', ' ')}")

if __name__ == "__main__":
    asyncio.run(main())