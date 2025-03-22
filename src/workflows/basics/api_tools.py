import json
import logging
import os
import sys
from typing import Any, Dict

import requests
from pydantic import BaseModel, Field

from util.utils import call_tool, execute_tool, parse_tool_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# https://platform.openai.com/docs/assistants/tools/function-calling
# Based on https://github.com/daveebbelaar/ai-cookbook/blob/main/patterns/workflows/1-introduction/3-tools.py

# --------------------------------------------------------------
# Data Model
# --------------------------------------------------------------


class WeatherResponse(BaseModel):
    """Response model for weather information."""

    temperature: float = Field(
        description="The current temperature in celsius for the given location."
    )
    response: str = Field(
        description="A natural language response to the user's question."
    )


# --------------------------------------------------------------
# Tools
# --------------------------------------------------------------


def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get weather data for a given location using the Open-Meteo API.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Dictionary containing current weather data

    Raises:
        requests.RequestException: If the API request fails
    """
    try:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        response.raise_for_status()
        data = response.json()
        return data["current"]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch weather data: {str(e)}")
        raise


# --------------------------------------------------------------
# Workflow
# --------------------------------------------------------------


def process_weather_query(system_prompt: str, user_prompt: str) -> WeatherResponse:
    """Process a weather query using the OpenAI API and weather tools.

    Args:
        system_prompt: System prompt for the AI
        user_prompt: User's weather query

    Returns:
        WeatherResponse object containing temperature and natural language response

    Raises:
        Exception: If any step of the process fails
    """
    try:
        # Initialize messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Get tools
        tools = {
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

        # Get initial response with tool calls
        response = call_tool(messages, tools)
        logger.info("Received initial response with tool calls")

        # Execute tools and get results
        messages = execute_tool(response, messages, {"get_weather": get_weather})
        logger.info("Executed weather tools and got results")

        # Parse final response
        result = parse_tool_response(messages, tools, WeatherResponse)
        logger.info("Successfully parsed weather response")

        return result

    except Exception as e:
        logger.error(f"Error processing weather query: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        system_prompt = "You are a helpful weather assistant."
        user_prompt = "What's the weather like in Seattle today?"

        result = process_weather_query(system_prompt, user_prompt)

        print("\nWeather Information:")
        print("-" * 20)
        print(f"Temperature: {result.temperature}°C")
        print(f"Response: {result.response}")

    except Exception as e:
        logger.error(f"Failed to process weather query: {str(e)}")
        sys.exit(1)
