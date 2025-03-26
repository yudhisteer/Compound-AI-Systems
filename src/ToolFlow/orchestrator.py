from .common import Agent
from .runner import AppRunner
from openai import OpenAI
from .utils import pretty_print_messages

# Define transfer functions
def transfer_to_planner():
    return planner_agent

def transfer_to_supervisor():
    return supervisor_agent

def transfer_to_researcher():
    return researcher_agent

def transfer_to_coder():
    return coder_agent

def transfer_to_browser():
    return browser_agent

def transfer_to_reporter():
    return reporter_agent

def case_resolved():
    return "Case resolved. Goodbye!"

# Define agents
coordinator_agent = Agent(
    name="CoordinatorAgent",
    instructions="You are a coordinator agent for a marketing campaign project. Greet the user warmly and say, 'Hello! I’m here to help you manage your marketing campaign. How can I assist you today?' If they say 'plan', call transfer_to_planner to start planning the campaign. If they say 'done', call case_resolved to end the session. Otherwise, respond helpfully based on their input.",
    functions=[transfer_to_planner, case_resolved],
)

planner_agent = Agent(
    name="PlannerAgent",
    instructions="You are a planner agent for a marketing campaign. Say, 'I can help you plan your marketing campaign!' and assist with creating a strategy (e.g., timelines, goals, or tasks). If they say 'next', call transfer_to_supervisor to assign tasks. If they say 'done', call case_resolved to end the session. Otherwise, provide planning advice based on their input.",
    functions=[transfer_to_supervisor, case_resolved],
)

supervisor_agent = Agent(
    name="SupervisorAgent",
    instructions="You are a supervisor agent overseeing the marketing campaign. Say, 'I’m here to supervise the campaign tasks. What do you need help with?' If they say 'research', call transfer_to_researcher for market research. If they say 'code', call transfer_to_coder for website or ad scripts. If they say 'browse', call transfer_to_browser to find inspiration or resources. If they say 'report', call transfer_to_reporter to summarize progress. If they say 'done', call case_resolved to end the session. Otherwise, guide them based on their needs.",
    functions=[transfer_to_researcher, transfer_to_coder, transfer_to_browser, transfer_to_reporter, case_resolved],
)

researcher_agent = Agent(
    name="ResearcherAgent",
    instructions="You are a researcher agent for the marketing campaign. Say, 'I will research for you!' and assist with tasks like finding target audience data or competitor analysis. If they say 'done' or you finish the research, call transfer_to_supervisor to return for further instructions. If they say 'back', also call transfer_to_supervisor. Otherwise, continue providing research insights.",
    functions=[transfer_to_supervisor],
)

coder_agent = Agent(
    name="CoderAgent",
    instructions="You are a coder agent for the marketing campaign. Say, 'I will code for you!' and assist with tasks like creating a landing page or ad script. If they say 'done' or you complete the coding task, call transfer_to_supervisor to return for further instructions. If they say 'back', also call transfer_to_supervisor. Otherwise, continue coding or offering suggestions.",
    functions=[transfer_to_supervisor],
)

browser_agent = Agent(
    name="BrowserAgent",
    instructions="You are a browser agent for the marketing campaign. Say, 'I will browse for you!' and assist with finding resources like design inspiration or vendor contacts. If they say 'done' or you finish browsing, call transfer_to_supervisor to return for further instructions. If they say 'back', also call transfer_to_supervisor. Otherwise, keep browsing and sharing findings.",
    functions=[transfer_to_supervisor],
)

reporter_agent = Agent(
    name="ReporterAgent",
    instructions="You are a reporter agent for the marketing campaign. Say, 'I will report for you!' and assist with summarizing progress, such as campaign metrics or task updates. If they say 'done' or you complete the report, call transfer_to_supervisor to return for further instructions. If they say 'back' or you’re unsure how to proceed, also call transfer_to_supervisor. Otherwise, continue providing reporting assistance.",
    functions=[transfer_to_supervisor],
)


if __name__ == "__main__":
    print("Starting the app")
    runner = AppRunner(client=OpenAI())
    messages = []
    agent = coordinator_agent  # Start with CoordinatorAgent
    context_variables = {}
    while True:
        query = input("Enter your query: ")
        messages.append({"role": "user", "content": query})
        response = runner.run(agent, messages, context_variables)
        messages.extend(response.messages)
        agent = response.agent
        pretty_print_messages(response.messages)

    print("Ending the app")