import json
import os
import sys

import requests
from pydantic import BaseModel, Field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.utils.utils import call_tools, parse_tools_response

# https://platform.openai.com/docs/assistants/tools/function-calling
# Based on https://github.com/daveebbelaar/ai-cookbook/blob/main/patterns/workflows/1-introduction/3-tools.py


class WeatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius for the given location."
    )
    response: str = Field(
        description="A natural language response to the user's question."
    )


def get_weather(latitude: float, longitude: float) -> dict:
    """This is a publically available API that returns the weather for a given location.

    Output format:
    {
    'time': '2025-02-28T19:45',
    'interval': 900,
    'temperature_2m': 10.2,
    'wind_speed_10m': 20.3
    }
    """
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]


def call_function(name: str, args: dict) -> dict:
    if name == "get_weather":
        return get_weather(**args)
    else:
        raise ValueError(f"Function {name} not found")


if __name__ == "__main__":
    system_prompt = "You are a helpful weather assistant."
    user_prompt = "What's the weather like in Seattle today?"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current temperature for provided coordinates in celsius.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                    },
                    "required": ["latitude", "longitude"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]

    # ------------------ Model knows to call the function -------------------#
    response = call_tools(messages, tools)
    print(
        "Response:", response, "\n"
    )  # model provides the tool call id and the function name and the longitude and latitude args

    # print(response.model_dump())
    # print(response.choices[0].message.tool_calls) # [ChatCompletionMessageToolCall(id='call_bnZManuFi76uwRm7N4gAEGUn', function=Function(arguments='{"latitude":47.6062,"longitude":-122.3321}', name='get_weather'), type='function')]

    # ------------------ We now execute the function and get the result ------------------#
    ### Note: We are executing the function and not the model
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
        result = call_function(
            function_name, function_args
        )  # {'time': '2025-02-28T20:00', 'interval': 900, 'temperature_2m': 10.0, 'wind_speed_10m': 3.1}
        # Add the result to the messages
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )
    print("messages:", messages, "\n")

    # ------------------ We now parse the result ------------------#
    result = parse_tools_response(messages, tools, WeatherResponse)
    print("Temperature:", result.temperature)
    print("Response:", result.response)
