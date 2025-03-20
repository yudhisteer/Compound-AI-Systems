from .common import Agent, Tool
from .tools import calculator_tool, date_tool, people_search_tool


def __get_tools(agent: Agent) -> str:
    """
    Helper function to get the tools from the agent.
    Example output:
        ```
        people_search - Search for information about people
        calculator - Perform mathematical calculations
        weather_lookup - Get current weather conditions
        ```
    Will be used to create the prompt for the LLM to choose the tool.
    """
    # check if the tool is a tool and not an Agent
    tools = [tool for tool in agent.functions if isinstance(tool, Tool)]
    print("tools: ", tools)
    # Create a list that combines the name and description of each tool
    str_tools = [tool.name + " - " + tool.desc for tool in tools]
    print("str_tools: ", str_tools)
    # Join the strings in the list with a newline character.
    return "\n".join(str_tools)



main_agent = Agent(
    name="MainAgent",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    functions=[people_search_tool, calculator_tool, date_tool],
)


if __name__ == "__main__":
    print(__get_tools(main_agent))

