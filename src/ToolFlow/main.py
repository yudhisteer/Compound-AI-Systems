import os

from openai import OpenAI

from .common import Agent, AgentConfig


open_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

main_agent = Agent(
    name="MainAgent",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    functions=[],
)

if __name__ == "__main__":
    ...