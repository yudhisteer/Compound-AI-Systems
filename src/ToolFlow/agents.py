from .common import Agent
from .prompts import (
    FLIGHT_CANCELLATION_POLICY,
    FLIGHT_CHANGE_POLICY,
    FLIGHT_MODIFICATION_POLICY,
    LOST_BAGGAGE_POLICY,
    STARTER_PROMPT,
)
from .tools import (
    case_resolved,
    change_flight,
    escalate_to_human,
    initiate_baggage_search,
    initiate_flight_credits,
    initiate_refund,
    valid_to_change_flight,
)

# ---------------------------------
# Routing functions
# ---------------------------------


def triage_instructions(context_variables: dict) -> str:
    customer_context = context_variables.get("customer_context", None)
    flight_context = context_variables.get("flight_context", None)
    return f"""You are to triage a users request, and call a tool to transfer to the right intent.
    Once you are ready to transfer to the right intent, call the tool to transfer to the right intent.
    You dont need to know specifics, just the topic of the request.
    When you need more information to triage the request to an agent, ask a direct question without explaining why you're asking it.
    Do not share your thought process with the user! Do not make unreasonable assumptions on behalf of user.
    The customer context is here: {customer_context}, and flight context is here: {flight_context}"""


def transfer_to_lost_baggage():
    return lost_baggage_agent


def transfer_to_triage():
    return triage_agent


def transfer_to_flight_modification():
    return flight_modification_agent


def transfer_to_flight_cancel():
    return flight_cancel_agent


def transfer_to_flight_change():
    return flight_change_agent


# ---------------------------------
# Agents
# ---------------------------------

triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_instructions,
    functions=[transfer_to_lost_baggage, transfer_to_flight_modification],
)


lost_baggage_agent = Agent(
    name="Lost Baggage Agent",
    instructions=STARTER_PROMPT + LOST_BAGGAGE_POLICY,
    functions=[
        escalate_to_human,
        initiate_baggage_search,
        transfer_to_triage,
        case_resolved,
    ],
)


flight_cancel_agent = Agent(
    name="Flight cancel Agent",
    instructions=STARTER_PROMPT + FLIGHT_CANCELLATION_POLICY,
    functions=[
        escalate_to_human,
        initiate_refund,
        initiate_flight_credits,
        transfer_to_triage,
        case_resolved,
    ],
)


flight_modification_agent = Agent(
    name="Flight Modification Agent",
    instructions=FLIGHT_MODIFICATION_POLICY,
    functions=[transfer_to_flight_cancel, transfer_to_flight_change],
    parallel_tool_calls=False,
)


flight_change_agent = Agent(
    name="Flight change Agent",
    instructions=STARTER_PROMPT + FLIGHT_CHANGE_POLICY,
    functions=[
        escalate_to_human,
        change_flight,
        valid_to_change_flight,
        transfer_to_triage,
        case_resolved,
    ],
)
