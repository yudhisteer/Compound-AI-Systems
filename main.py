import os
from openai import OpenAI
from src.ReAct.common import Agent, AgentConfig
from src.ReAct.reactexecutor import ReactExecutor
open_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


main_agent = Agent(
    name="Main Agent",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
)

if __name__ == "__main__":
    query = "What is the capital of France?"
    agent_config = AgentConfig().with_model_client(open_ai).with_token_limit(5000).with_max_interactions(5)
    react_executor = ReactExecutor(main_agent, agent_config)
    response = react_executor.execute(query)
    print(response)


