import json
import os
from openai import OpenAI
from src.shared.utils import debug_print

# From: https://github.com/daveebbelaar/ai-cookbook/blob/main/mcp/crash-course/5-mcp-vs-function-calling/function-calling.py

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


"""
This is a simple example to demonstrate that MCP simply enables a new way to call functions.
"""

def calculate_sum(a: int, b: int) -> int:
    """Returns the sum of two numbers"""
    return a + b

def calculate_product(a: int, b: int) -> int:
    """Returns the product of two numbers"""
    return a * b

# Define tools for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_sum",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "First number"},
                    "b": {"type": "integer", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_product",
            "description": "Multiply two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "First number"},
                    "b": {"type": "integer", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
]


query = "Calculate 25 + 17"

# Call LLM
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": query}],
    tools=tools,
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    debug_print(f"Tool Call: {tool_call}") # Tool Call: ChatCompletionMessageToolCall(id='call_y7llbugRF5WJkiF3KJIhhP3x', function=Function(arguments='{"a":25,"b":17}', name='calculate_sum'), type='function')
    tool_name = tool_call.function.name
    debug_print(f"Tool Name: {tool_name}") # Tool Name: calculate_sum
    tool_args = json.loads(tool_call.function.arguments)
    debug_print(f"Tool Args: {tool_args}") # Tool Args: {'a': 25, 'b': 17}

    # Execute directly
    result = calculate_sum(**tool_args)
    debug_print(f"Result: {result}") # Result: 42

    messages=[
            {"role": "user", "content": query},
            response.choices[0].message,
            {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)},
        ]
    debug_print(f"Messages: {messages}")

    # Send result back to model
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": query},
            response.choices[0].message,
            {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)},
        ],
    )
    print(final_response.choices[0].message.content)