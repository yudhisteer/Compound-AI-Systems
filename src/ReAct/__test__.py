import inspect

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


# A sample function that might be wrapped as a tool
def calculate_area(length, width, units="meters"):
    """Calculate the area of a rectangle."""
    return f"The area is {length * width} square {units}"


if __name__ == "__main__":
    print(__get_tools(main_agent))

    print("\n================================================")
    # Getting and using the signature
    signature = inspect.signature(calculate_area)

    # Print the full signature
    print(f"Function signature: {signature}")  # Output: (length, width, units='meters')
    print(f"Function signature parameters: {signature.parameters}")
    for param in signature.parameters:
        print(f"Parameter: {param}")

    # Get parameter names
    param_names = list(signature.parameters.keys())
    print(f"Parameter names: {param_names}")  # Output: ['length', 'width', 'units']

    # Check which parameters are required (don't have default values)
    required_params = [
        name
        for name, param in signature.parameters.items()
        if param.default is param.empty
    ]
    print(f"Required parameters: {required_params}")  # Output: ['length', 'width']

    # Check parameter details individually
    for name, param in signature.parameters.items():
        print(
            f"{name}: default={param.default if param.default is not param.empty else 'REQUIRED'}"
        )

    print("\n================================================")
    prompt = f"""To Answer the following request as best you can:.
    Determine the inputs to send to the tool:
    Given that the function signature of the tool function is: {inspect.signature(calculate_area)}.

    CONTEXT HISTORY:
    ---
    """
    parameters = inspect.signature(calculate_area).parameters
    prompt += f"""RESPONSE FORMAT:
                {{
                    {', '.join([f'"{param}": <function parameter>' for param in parameters])}
                }}"""
    print(prompt)

    # Output from LLM:
    # {
    # "length": 10,
    # "width": 5,
    # "units": "feet"
    # }
    print("\n================================================")
    import json

    response = """{
    "length": 10,
    "width": 5,
    "units": "feet"
    }"""
    response = json.loads(response)
    print(response)
    print(type(response))
