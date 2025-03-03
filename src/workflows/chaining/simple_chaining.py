import os

from openai import OpenAI

# Based on: https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/basic_workflows.ipynb

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"


def get_chat_completion(
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
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can answer questions and help with tasks.",
                },
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


if __name__ == "__main__":

    data_processing_steps = [
        """Extract all store units and their sales numbers.
    Format as 'store: units'.
    Example:
    NY: 123 units
    LA: 46 units""",
        """Standardize all numbers to thousands (K).
    Format as 'store: number K'.
    Example:
    NY: 0.12K
    LA: 0.046K""",
        """Rearrange the data in ascending order of units sold.
    Format as 'store: units'.
    Example:
    NY: 10K units
    LA: 46K units""",
        """Generate sales analysis table:
    | Store | Units (K) |
    | NY    | 0.16K     |
    | LA    | 0.046K    |""",
    ]

    report = """Q1 Sales Report:
    NY store sold 15600 units
    LA store sold 23400 units
    Miami store sold 8900 units
    Chicago store sold 17800 units
    Houston store sold 20300 units"""

    print("Starting chain workflow...\n\nReport:\n", report)

    result = chain_workflow(report, data_processing_steps, debug=True)
    print("\n\nResult:\n", result)
