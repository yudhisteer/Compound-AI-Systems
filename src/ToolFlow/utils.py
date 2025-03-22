import inspect
import json
from datetime import datetime
from typing import Callable

# From: https://github.com/apssouza22/ai-agent-react-llm/blob/version-2/src/version2


def debug_print(*args: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")


def function_to_json(func: Callable) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.

    Args:
        func: The function to be converted.

    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


def pretty_print_messages(messages) -> None:
    for message in messages:
        if message["role"] != "assistant":
            continue

        # print agent name in blue
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # print response, if any
        if message["content"]:
            print(message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


if __name__ == "__main__":

    # Example function
    def calculate_area(
        shape: str, length: float, width: float = None, radius: float = None
    ) -> float:
        """
        Calculate the area of a geometric shape.

        Args:
            shape: The type of shape ('rectangle', 'circle', or 'square')
            length: The length for rectangles or side length for squares
            width: The width for rectangles (optional)
            radius: The radius for circles (optional)

        Returns:
            The calculated area of the shape
        """
        if shape == "rectangle" and width is not None:
            return length * width
        elif shape == "square":
            return length * length
        elif shape == "circle" and radius is not None:
            import math

            return math.pi * radius * radius
        else:
            raise ValueError("Invalid shape or missing required parameters")

    function_json = function_to_json(calculate_area)
    print(json.dumps(function_json, indent=2))

    # Ouput example:
    #     {
    #   "type": "function",
    #   "function": {
    #     "name": "calculate_area",
    #     "description": "\n        Calculate the area of a geometric shape.\n        \n        Args:\n            shape: The type of shape ('rectangle', 'circle', or 'square')\n            length: The length for rectangles or side length for squares\n            width: The width for rectangles (optional)\n            radius: The radius for circles (optional)\n        \n        Returns:\n            The calculated area of the shape\n        ",
    #     "parameters": {
    #       "type": "object",
    #       "properties": {
    #         "shape": {
    #           "type": "string"
    #         },
    #         "length": {
    #           "type": "number"
    #         },
    #         "width": {
    #           "type": "number"
    #         },
    #         "radius": {
    #           "type": "number"
    #         }
    #       },
    #       "required": [
    #         "radius": {
    #           "type": "number"
    #         }
    #       },
    #         "radius": {
    #           "type": "number"
    #         }
    #         "radius": {
    #           "type": "number"
    #         "radius": {
    #         "radius": {
    #           "type": "number"
    #         }
    #       },
    #       "required": [
    #         "shape",
    #         "length"
    #       ]
    #      }
    #         }
    #     }

    # Simple message
    debug_print("Starting application")

    # Multiple arguments get joined with spaces
    debug_print("Processing file:", "data.csv")

    # You can include variables
    user_id = 12345
    status = "active"
    debug_print("User", user_id, "is", status)

    # Include numeric values
    debug_print("Processed", 150, "records in", 2.5, "seconds")

    # Error messages
    try:
        result = 10 / 0
    except Exception as e:
        debug_print("Error occurred:", str(e))

    messages = [
        {"role": "user", "content": "Can you search for information about Python?"},
        {
            "role": "assistant",
            "sender": "ResearchAgent",
            "content": "I'll search for information about Python for you.",
        },
        {
            "role": "assistant",
            "sender": "ResearchAgent",
            "content": "Let me search for that information.",
            "tool_calls": [
                {
                    "function": {
                        "name": "search_web",
                        "arguments": '{"query": "Python programming language", "max_results": 5}',
                    }
                }
            ],
        },
        {
            "role": "assistant",
            "sender": "DataAnalysisAgent",
            "content": "I'll analyze this data for you.",
            "tool_calls": [
                {
                    "function": {
                        "name": "load_dataset",
                        "arguments": '{"file_path": "data.csv"}',
                    }
                },
                {
                    "function": {
                        "name": "calculate_statistics",
                        "arguments": '{"columns": ["price", "quantity"], "operation": "mean"}',
                    }
                },
            ],
        },
    ]

    pretty_print_messages(messages)
