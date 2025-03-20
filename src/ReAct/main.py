import os

from openai import OpenAI

from .common import Agent, AgentConfig
from .reactexecutor import ReactExecutor

from .tools import calculator_tool, date_tool, people_search_tool

open_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

main_agent = Agent(
    name="MainAgent",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    functions=[people_search_tool, calculator_tool, date_tool],
)

if __name__ == "__main__":
    query = "What is the half of Einstien's age?"
    agent_config = (
        AgentConfig()
        .with_model_client(open_ai)
        .with_token_limit(5000)
        .with_max_interactions(5)
    )
    react_executor = ReactExecutor(main_agent, agent_config)
    response = react_executor.execute(query)
    print(response)
