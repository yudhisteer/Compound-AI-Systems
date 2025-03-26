from .common import Agent
from .runner import AppRunner
from openai import OpenAI
from .utils import pretty_print_messages, debug_print
from pydantic import BaseModel
from enum import Enum
from typing import Literal


class SupportResponse(BaseModel):
    response: str
    action: Literal["continue_helping", "resolve_case"]

    def __str__(self) -> str:
        print(f"[DEBUG] Action chosen: {self.action}")  # Debug print to see the action
        return self.response

# Define transfer functions
def transfer_to_support():
    return support_agent

# Define case resolved function
def case_resolved():
    return "Case resolved. Goodbye!"

# Define agents
greeting_agent = Agent(
    name="GreetingAgent",
    instructions="You are a greeting agent. Greet the user and ask how you can help. If they say 'help' or 'support', call transfer_to_support. Otherwise, respond normally.",
    functions=[transfer_to_support],
    response_format=None,  # Will use create
)

support_agent = Agent(
    name="SupportAgent",
    instructions="You are a support agent. Assist the user with their questions. When responding, choose 'continue_helping' if the user needs more assistance, or 'resolve_case' if they say 'done' or the conversation is complete. Always provide helpful and friendly support messages.",
    response_format=SupportResponse,  # Will use parse - no tool_calls for parsed responses
)

# Run the workflow
if __name__ == "__main__":
    print("Starting the app")
    runner = AppRunner(client=OpenAI())
    messages = []
    agent = greeting_agent
    context_variables = {}  # No context variables needed for this simple example
    while True:
        query = input("Enter your query: ")
        messages.append({"role": "user", "content": query})
        response = runner.run(agent, messages, context_variables)
        messages.extend(response.messages)
        agent = response.agent
        debug_print(f"Agent: {agent.name}")
        # debug_print("Current message history:", messages)
        pretty_print_messages(response.messages)
        # Check for case_resolved to end the conversation
        if any(msg["role"] == "tool" and msg["tool_name"] == "case_resolved" for msg in response.messages):
            break
    print("Finishing the app")