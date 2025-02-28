import os
import sys
import json
import requests
from pydantic import BaseModel, Field
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.utils.utils import call_tool, parse_tool_response
from src.utils.utils import execute_tool, call_function

# https://platform.openai.com/docs/assistants/tools/function-calling
# Based on https://github.com/daveebbelaar/ai-cookbook/blob/main/patterns/workflows/1-introduction/3-tools.py

class DBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    id: int = Field(description="The record id of the answer.")

def search_db(question: str):
    # Using os.path.join for proper path handling across platforms
    data_path = os.path.join("src", "workflows", "basics", "data.json")
    with open(data_path, "r") as f:
        return json.load(f)


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

    #------------------ Model knows to call the function -------------------#
    response = call_tool(messages, tools)
    # print("Response:", response)

    #------------------ Model provides the tool call id and the function name and the content -------------------#
    messages = execute_tool(response, messages, function_registry)
    # print("Messages:", messages)

    #------------------ Parse the result ------------------#
    result = parse_tool_response(messages, tools, DBResponse)
    print("ID:", result.id)
    print("Answer:", result.answer)

