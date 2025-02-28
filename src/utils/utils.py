import os
import json 
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

# Load environment variables
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")
client = OpenAI(api_key=api_key)



def call_tool(
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


def parse_tool_response(
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


def get_chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0,
) -> str:
    """
    Get a chat completion from OpenAI.

    Args:
        prompt: The text prompt to send
        model: The model to use (default: gpt-4)
        temperature: Controls randomness (0-1, default: 0)

    Returns:
        The completion text
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Error getting chat completion: {str(e)}")




def chain_workflow(query: str, steps: list[str], debug: bool = False) -> str:
    """
    Execute a chain of workflows.
    """
    input_query = query
    for i, step in enumerate(steps):
        input_prompt = f"Step {i+1}:\n{step}\n\nQuery:\n{input_query}"
        input_query = get_chat_completion(input_prompt)
        if debug:
            print("-" * 80)
            print(f"Step {i+1}:\n{step}\n\nResult:\n{input_query}\n\n")
    return input_query


def execute_tool(response: ChatCompletion, messages: list[dict], function_registry: dict):
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
        function_name = tool_call.function.name # get_weather
        # Get the arguments  
        function_args = json.loads(tool_call.function.arguments) #{'latitude': 47.6062, 'longitude': -122.3321}
        # Add the tool call to the messages
        messages.append(response.choices[0].message)
        # Execute the function
        result = call_function(function_name, function_args, function_registry) # {'time': '2025-02-28T20:00', 'interval': 900, 'temperature_2m': 10.0, 'wind_speed_10m': 3.1}
        # Add the result to the messages
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
    return messages


def call_function(name: str, args: dict, function_registry: dict) -> dict:
    """
    Call a function from the function registry.
    """
    if name in function_registry:
        return function_registry[name](**args)
    else:
        raise ValueError(f"Function {name} not found")