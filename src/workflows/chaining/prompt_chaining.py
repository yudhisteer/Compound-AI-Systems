import logging
import os
from datetime import datetime
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

# Based on: https://github.com/daveebbelaar/ai-cookbook/blob/main/patterns/workflows/2-workflow-patterns/1-prompt-chaining.py

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"


# -------------------------------- Data Models --------------------------------#


class EventExtraction(BaseModel):
    """First LLM call: Extract basic event information"""

    description: str = Field(description="Raw description of the event")
    is_reservation_event: bool = Field(description="Whether this text describes a reservation event")
    confidence_score: float = Field(description="Confidence score between 0 and 1")


class EventDetails(BaseModel):
    """Second LLM call: Parse specific event details"""

    name: str = Field(description="Name of the person making the reservation")
    date: str = Field(description="Date and time of the reservation. Use ISO 8601 to format this value.")
    event_name: str = Field(description="Name of the event")
    participants: int = Field(description="Number of people in the reservation")
    reservation_request: Optional[str] = Field(description="Specific reservation request made by the user")


class EventConfirmation(BaseModel):
    """Third LLM call: Generate confirmation message"""

    confirmation_message: str = Field(description="Natural language confirmation message")


# -------------------------------- Functions  --------------------------------#


def extract_event_info(user_input: str) -> EventExtraction:
    """First LLM call to determine if input is a reservation event"""
    logger.info("Starting reservation extraction analysis")
    logger.debug(f"Input text: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Analyze if the text describes a reservation event.",
            },
            {"role": "user", "content": user_input},
        ],
        response_format=EventExtraction,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Extraction complete - Is reservation event: {result.is_reservation_event}, Confidence: {result.confidence_score:.2f}"
    )
    return result


def parse_event_details(description: str) -> EventDetails:
    """Second LLM call to extract specific reservation details"""
    logger.info("Starting reservation details parsing")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference.",
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )
    result = completion.choices[0].message.parsed

    logger.info(
        f"""Parsed reservation details - Name: {result.name}, 
                Date: {result.date}, 
                Event Name: {result.event_name}, 
                Participants: {result.participants}, 
                Reservation Request: {result.reservation_request}"""
    )

    return result


def generate_confirmation(event_details: EventDetails) -> EventConfirmation:
    """Third LLM call to generate a confirmation message"""
    logger.info("Generating confirmation message")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Generate a natural confirmation message for the event. Sign of with your name; Jean-Philippe",
            },
            {"role": "user", "content": str(event_details.model_dump())},
        ],
        response_format=EventConfirmation,
    )
    result = completion.choices[0].message.parsed

    logger.info("Confirmation message generated successfully")

    return result


# -------------------------------- Chain Workflow  --------------------------------#


def process_reservation_request(user_input: str):
    """Main function implementing the prompt chain with gate check"""
    logger.info("Processing reservation request")
    logger.debug(f"Raw input: {user_input}")

    # First LLM call: Extract basic info
    initial_extraction = extract_event_info(user_input)

    # Gate check: Verify if it's a reservation event with sufficient confidence
    if (
        not initial_extraction.is_reservation_event
        or initial_extraction.confidence_score < 0.7
    ):
        logger.warning(
            f"Gate check failed - is_reservation_event: {initial_extraction.is_reservation_event}, confidence: {initial_extraction.confidence_score:.2f}"
        )
        return None

    logger.info("Gate check passed, proceeding with event processing")

    # Second LLM call: Get detailed reservation information
    event_details = parse_event_details(initial_extraction.description)

    # Third LLM call: Generate confirmation
    confirmation = generate_confirmation(event_details)

    logger.info("Reservation request processing completed successfully")

    return confirmation


if __name__ == "__main__":

    user_input = """Hi, this is Michael Johnson. I'd like to reserve a table for 8 people at Botanica Restaurant for next Friday at 7pm. 
                   We're celebrating my daughter's graduation and would appreciate a quiet corner table if available."""

    invalid_input = "What is the weather in Tokyo?"

    result = process_reservation_request(user_input)
    if result:
        print(f"Confirmation: {result.confirmation_message}")
    else:
        print("This doesn't appear to be a reservation request.")
