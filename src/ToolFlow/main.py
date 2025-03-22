import os

from openai import OpenAI

from .common import Agent
from .types import TaskResponse

open_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

main_agent = Agent(
    name="MainAgent",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    functions=[],
)

context_variables = {
    "user_id": 12345,
    "status": "active",
    "processed_records": 150,
    "processing_time": 2.5,
}

class AppRunner:
    def __init__(self, client: OpenAI):
        self.client = client

    def run(self, query:str, agent:Agent, context_variables:dict, messages:list):
        return TaskResponse()

if __name__ == "__main__":
    print("Starting the application...")
    app_runner = AppRunner(client=open_ai)
    messages = []
    while True:
        query = "What is the capital of France?"
        response = app_runner.run(query, main_agent, context_variables, messages)
        messages.extend(response.messages)
        agent = response.agent
        break

    print("Application finished.")
