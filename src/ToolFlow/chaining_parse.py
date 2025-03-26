from .common import Agent
from .runner import AppRunner
from openai import OpenAI
from .utils import pretty_print_messages, debug_print
from pydantic import BaseModel
from typing import Literal, Any
from .runner import TaskResponse

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


def switch_agent_parser(response: TaskResponse, 
                       pydantic_attribute: str, 
                       expected_value: Any, 
                       next_agent: Agent) -> Agent:
    # Check if the response has a parsed_response (Pydantic object)
    if response.parsed_response:
        # get the attribute value from the parsed response
        attribute_value = getattr(response.parsed_response, pydantic_attribute, None)
        debug_print(f"[DEBUG] Attribute Value: {attribute_value}, Expected: {expected_value}")
        # if the attribute value is the expected value, return the next agent
        if attribute_value == expected_value:
            debug_print(f"[DEBUG] Parsed Response: {attribute_value}")
            debug_print(f"[DEBUG] Switching to {next_agent.name}")
            return next_agent
        return response.agent  # Return current agent if condition not met
    else:
        return response.agent  # Return current agent if no parsed_response

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

        # Switch agent
        agent = switch_agent_parser(
            response=response, 
            pydantic_attribute="action", 
            expected_value="resolve_case", 
            next_agent=greeting_agent,
        )
                
        debug_print(f"Agent: {agent.name}")
        pretty_print_messages(response.messages)
        
        if any(msg["role"] == "tool" and msg["tool_name"] == "case_resolved" for msg in response.messages):
            break
            
    print("Finishing the app")