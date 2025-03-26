from .common import Agent
from .runner import AppRunner
from openai import OpenAI
from .utils import pretty_print_messages, debug_print

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
)

support_agent = Agent(
    name="SupportAgent",
    instructions="You are a support agent. Assist the user with their questions. If they say 'done', call case_resolved. Otherwise, respond normally.",
    functions=[case_resolved],
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
        agent = response.agent # update the active agent
        debug_print(f"Agent: {agent.name}")
        debug_print("Current message history:", messages)
        pretty_print_messages(response.messages)

    print("Finishing the app")

