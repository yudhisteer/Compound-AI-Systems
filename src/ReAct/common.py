from pydantic import BaseModel, Field
from typing import Callable, List, Union
from openai import OpenAI
# --------------------------------------------------------------
# Data Model
# --------------------------------------------------------------

class ToolChoice(BaseModel):
    """
    Data model for the tool choice
    """
    tool_name: str = Field(description="The name of the tool to use.")
    reason_of_choice: str = Field(description="The reasoning for choosing the tool.")


class ReactEnd(BaseModel):
    """
    Data model for the observation step
    """
    stop: bool= Field(..., description="True if the context is enough to answer the request else False")
    final_answer: str = Field(..., description="Final answer is the context is enough to answer the request")
    confidence: float = Field(..., description="Confidence score of the final answer between 0 and 1")


class Tool:
    def __init__(self, name: str, func: Callable, desc: str) -> None:
        self.desc = desc
        self.func = func
        self.name = name

class Agent(BaseModel):
    """
    An agent is a function that can be called by the LLM.
    Attributes:
        name (str): Name of the agent. Defaults to "Agent".
        model (str): The model identifier. Defaults to "gpt-4o-mini".
        instructions (Union[str, Callable[[], str]]): Instructions for the agent. Can be either:
            - A static string: Direct instructions for the agent
            - A callable: A function that returns a string, allowing for dynamic instruction generation
        functions (List): List of available functions. Defaults to empty list.

    Examples:
        # Using static instructions
        agent1 = Agent(
            name="SimpleAgent",
            model="gpt-4o-mini",
            instructions="You are a helpful assistant that specializes in Python"
        )

        # Using dynamic instructions
        def get_dynamic_instructions():
            current_time = datetime.now()
            return f"You are a helpful assistant. Current time is {current_time}"

        agent2 = Agent(
            name="DynamicAgent",
            model="gpt-4o-mini",
            instructions=get_dynamic_instructions
        )
    """
    name: str = "Agent"
    model: str = "gpt-4o-mini"
    instructions: Union[str, Callable[[], str]] = "You are a helpful assistant"
    functions: List = []


class AgentConfig:
    def __init__(self):
        self.max_interactions = 3
        self.model = None
        self.token_limit: int = 5000

    def with_max_interactions(self, max_interactions: int):
        self.max_interactions = max_interactions
        return self

    def with_model_client(self, model: OpenAI):
        self.model = model
        return self
    
    def with_token_limit(self, token_limit: int):
        self.token_limit = token_limit
        return self
    

