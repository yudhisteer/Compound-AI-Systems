from typing import Callable, List, Union, Optional, Type

from openai import OpenAI
from pydantic import BaseModel, Field

from .utils import function_to_json

# --------------------------------------------------------------
# Data Model
# --------------------------------------------------------------


class ToolChoice(BaseModel):
    """
    Data model for the tool choice
    """

    tool_name: str = Field(description="The name of the tool to use.")
    reason_of_choice: str = Field(description="The reasoning for choosing the tool.")


class Tool:
    """
    Data model for the tool
    """

    def __init__(self, name: str, func: Callable, desc: str) -> None:
        self.desc = desc
        self.func = func
        self.name = name


class Agent(BaseModel):
    """
    Data model for the agent
    """

    name: str = "Agent"
    model: str = "gpt-4o-mini"
    instructions: Union[str, Callable[[], str]] = "You are a helpful agent."
    functions: List = []
    parallel_tool_calls: bool = True
    tool_choice: str = None
    response_format: Optional[Type[BaseModel]] = None

    def tools_in_json(self):
        return [function_to_json(f) for f in self.functions]

    def get_instructions(self, context_variables: dict = {}) -> str:
        if callable(self.instructions):
            return self.instructions(context_variables)
        return self.instructions


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
