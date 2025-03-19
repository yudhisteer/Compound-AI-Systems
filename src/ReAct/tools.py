from datetime import datetime
import wikipedia
from common import Tool, Agent

def perform_calculator(operation: str, a: int, b: int):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    return "Invalid operation"

def search_wikipedia(search_query: str):
    try:
        page = wikipedia.page(search_query)
        text = page.content
        return text[:300]
    except Exception as e:
        return (f"Could not find information about {search_query} on Wikipedia. Please try again with a different search query.")

def date_of_today():
    return datetime.date.today()


calculator_tool = Tool(
    name="calculator",
    func=perform_calculator,
    desc="Use this tool to perform calculations."
)

wikipedia_tool = Tool(
    name="wikipedia",
    func=search_wikipedia,
    desc="Use this tool to search information on Wikipedia."
)

date_tool = Tool(
    name="date",
    func=date_of_today,
    desc="Use this tool to get the current date."
)

people_search_agent = Agent(
    name="people_search_agent",
    instructions="You are a helpful assistant that can search for information about people.",
    #functions=[wikipedia_tool]
)

# We use an agent as a tool ( "tools using tools" or "agents using agents")
people_search_tool = Tool(
    name="people_search",
    func=people_search_agent,
    desc="Use this tool to search for information about people."
)
# we could give other tools to the agent such as google search, etc.
people_search_agent.functions = [wikipedia_tool]
