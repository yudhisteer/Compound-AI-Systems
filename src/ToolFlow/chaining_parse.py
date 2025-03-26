from .common import Agent
from .runner import AppRunner
from openai import OpenAI
from .utils import pretty_print_messages, debug_print
from pydantic import BaseModel
from typing import Literal, Any


class SupportResponse(BaseModel):
    response: str
    action: Literal["continue_helping", "resolve_case"]

# Define transfer functions
def transfer_to_support():
    return support_agent

def transfer_to_greeting():
    return greeting_agent

# Define case resolved function
def case_resolved():
    return "Case resolved. Goodbye!"

# Define agents
greeting_agent = Agent(
    name="GreetingAgent",
    instructions="You are a greeting agent. Greet the user and ask how you can help. If they say 'help' or 'support', call transfer_to_support. Otherwise, respond normally.",
    functions=[transfer_to_support],
    response_format=None,
)

support_agent = Agent(
    name="SupportAgent",
    instructions="You are a support agent. Assist the user with their questions. When responding, return a structured response with 'response' (your helpful message) and 'action' ('continue_helping' if the user needs more assistance, or 'resolve_case' if they say 'done' or the conversation is complete). Always provide helpful and friendly support messages.",
    functions=[],  # No tool calls needed since we're using parse()
    response_format=SupportResponse,
)


def handle_action(pydantic_attribute: Any, case: Any, current_agent: Agent, next_agent: Agent = greeting_agent) -> Agent:
    if pydantic_attribute == case:
        print(f"[DEBUG] Parsed Response: {pydantic_attribute}")
        print(f"[DEBUG] Returning to {next_agent.name}")
        return next_agent # return the next agent
    print(f"[DEBUG] Returning to {current_agent.name}")
    return current_agent  # Return current agent if condition not met

if __name__ == "__main__":
    print("Starting the app")
    runner = AppRunner(client=OpenAI())
    messages = []
    agent = greeting_agent
    context_variables = {}
    while True:
        query = input("Enter your query: ")
        messages.append({"role": "user", "content": query})
        response = runner.run(agent, messages, context_variables)
        messages.extend(response.messages)

        # check if the response is a pydantic object
        if response.parsed_response:
            agent = handle_action(
                pydantic_attribute=response.parsed_response.action, 
                case="resolve_case", 
                current_agent=response.agent,
                next_agent=greeting_agent,
            )
        # if the response is not a pydantic object, return the current agent
        else:
            agent = response.agent
        
        debug_print(f"Agent: {agent.name}")
        pretty_print_messages(response.messages)
        
        if any(msg["role"] == "tool" and msg["tool_name"] == "case_resolved" for msg in response.messages):
            break
            
    print("Finishing the app")