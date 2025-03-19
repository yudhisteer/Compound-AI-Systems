import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field

# https://platform.openai.com/docs/assistants/tools/function-calling
# Based on https://github.com/daveebbelaar/ai-cookbook/blob/main/patterns/workflows/1-introduction/3-tools.py

# --------------------------------------------------------------
# Setup OpenAI client
# --------------------------------------------------------------

# Load environment variables
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")
client = OpenAI(api_key=api_key)


# --------------------------------------------------------------
# Data Model
# --------------------------------------------------------------


class DBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    id: int = Field(description="The record id of the answer.")


# --------------------------------------------------------------
# Tools
# --------------------------------------------------------------


def search_db(question: str):
    data_path = os.path.join("src", "workflows", "basics", "data.json")
    with open(data_path, "r") as f:
        return json.load(f)


# --------------------------------------------------------------
# Private functions
# --------------------------------------------------------------


def _call_tool(
    messages: list[dict],
    tools: list[dict],
    model: str = "gpt-4o-mini",
    temperature: float = 0,
) -> str:
    """
    Send a request to OpenAI API with tool configurations and return the complete API response.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            tools=tools,
        )
        return response

    except Exception as e:
        raise Exception(f"Error getting chat completion: {str(e)}")


def _call_function(name: str, args: dict, function_registry: dict) -> dict:
    """
    Call a function from the function registry.
    """
    if name in function_registry:
        return function_registry[name](**args)
    else:
        raise ValueError(f"Function {name} not found")


def _execute_tool(
    response: ChatCompletion, messages: list[dict], function_registry: dict
):
    """
    Execute tool calls from an OpenAI API response and append results to messages.

    Args:
        response: The OpenAI API response containing tool calls
        messages: List of messages to append results to

    Returns:
        Updated messages list with tool call results
    """
    for tool_call in response.choices[0].message.tool_calls:
        # Get the function name
        function_name = tool_call.function.name  # get_weather
        # Get the arguments
        function_args = json.loads(
            tool_call.function.arguments
        )  # {'latitude': 47.6062, 'longitude': -122.3321}
        # Add the tool call to the messages
        messages.append(response.choices[0].message)
        # Execute the function
        result = _call_function(
            function_name, function_args, function_registry
        )  # {'time': '2025-02-28T20:00', 'interval': 900, 'temperature_2m': 10.0, 'wind_speed_10m': 3.1}
        # Add the result to the messages
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )
    return messages


def _parse_tool_response(
    messages: list[dict],
    tools: list[dict],
    response_format: BaseModel,
    model: str = "gpt-4o-mini",
    temperature: float = 0,
) -> str:
    """
    Parse an OpenAI API response into a structured Pydantic object.
    """
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=temperature,
            tools=tools,
            response_format=response_format,
        )
        return response.choices[0].message.parsed

    except Exception as e:
        raise Exception(f"Error getting chat completion: {str(e)}")


if __name__ == "__main__":
    system_prompt = "You are a helpful assistant that answers questions from the knowledge base about our e-commerce store."
    user_prompt = "How much student discount?"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Register the functions
    function_registry = {
        "search_db": search_db,
    }

    # Define the tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_db",
                "description": "Get the answer to the user's question from the knowledge base.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                    },
                    "required": ["question"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_numbers",
                "description": "Add numbers together.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {"type": "number"},
                        "num2": {"type": "number"},
                    },
                    "required": ["num1", "num2"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    ]

    # ------------------ Model knows to call the function -------------------#
    response = _call_tool(messages, tools)
    # print("Response:", response)

    # ------------------ Model provides the tool call id and the function name and the content -------------------#
    messages = _execute_tool(response, messages, function_registry)
    # print("Messages:", messages)

    # ------------------ Parse the result ------------------#
    result = _parse_tool_response(messages, tools, DBResponse)
    print("ID:", result.id)
    print("Answer:", result.answer)
