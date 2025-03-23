class OpenAIError(Exception):
    """
    Base exception class for OpenAI-related errors.

    This exception is raised when any error occurs during interaction
    with OpenAI services or APIs.

    Attributes:
        message (str): Human-readable error description
    """

    def __init__(self, message: str):
        self.message = message


class OpenAIRateLimitError(OpenAIError):
    """
    Exception raised when OpenAI API rate limits are exceeded.

    This specific error occurs when requests to OpenAI services
    exceed the allowed rate limits, indicating that the client
    should back off or reduce request frequency.
    """

    pass
