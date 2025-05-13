from typing import List

import requests

from ..common.config import OPENAI_BACKOFF, OPENAI_MAX_RETRIES
from ..common.http_retry import retry_with_exponential_backoff
from .utils import OpenAIError, OpenAIRateLimitError


class LLMClientInterface:
    """
    Abstract interface for LLM client implementations.

    This interface defines a standard contract that all LLM clients must fulfill,
    allowing for:

    Any concrete LLM client must implement the predict() method for text generation
    and the get_embeddings() method for vector embeddings.
    """

    def predict(self, messages: List[dict], max_tokens=1000, temperature=0.1):
        raise NotImplementedError

    def get_embeddings(self, input_text: str) -> List[list]:
        raise NotImplementedError


class OpenAPIClient(LLMClientInterface):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.base_url: str = "https://api.openai.com/v1"
        self.api_key: str = api_key
        self.model: str = model
        self.headers: dict = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry_with_exponential_backoff(
        backoff_in_seconds=OPENAI_BACKOFF,
        max_retries=OPENAI_MAX_RETRIES,
        errors=(OpenAIRateLimitError, OpenAIError),
    )
    def predict(
        self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1000
    ) -> str:
        """
        Predict the next message in the conversation.
        Ref: https://platform.openai.com/docs/api-reference/chat/create
        """
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        endpoint = "/chat/completions"
        response = requests.post(
            self.base_url + endpoint, headers=self.headers, json=data, timeout=60
        )

        # check if the response is not ok
        if not response.ok:
            openai_error: OpenAIError
            if response.status_code == 429:
                # rate limit error
                openai_error = OpenAIRateLimitError(response.text)
            else:
                # other error
                openai_error = OpenAIError(response.text)

            raise openai_error

        return response.json()

    def get_embeddings(self, input_param: List[str]) -> list[list]:
        """
        Get the embedding of a text.
        Ref: https://platform.openai.com/docs/api-reference/embeddings
        """
        data = {
            "input": input_param,
            "model": "text-embedding-ada-002",
        }
        endpoint = "/embeddings"
        response = requests.post(
            self.base_url + endpoint, headers=self.headers, json=data
        )
        if not response.ok:
            raise Exception(f"Failed to get embedding: {response.json()}")

        # response.json()["data"] is a list of dicts, each dict has a "embedding" key
        return [result["embedding"] for result in response.json()["data"]]
