import os
from typing import List

from core.common.config import OPENAI_API_KEY, OPENAI_API_MODEL
from core.llm.openapi_client import LLMClientInterface, OpenAPIClient


class LLMService:
    def __init__(self, llm_client: LLMClientInterface):
        self.llm_client = llm_client

    def predict(self, user_prompt: str):
        return self.llm_client.predict(
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt},
            ]
        )

    def get_embeddings(self, input_text: str):
        return self.llm_client.get_embeddings(input_text)


def llm_service_factory() -> LLMService:
    llm_client = OpenAPIClient(OPENAI_API_KEY, OPENAI_API_MODEL)
    return LLMService(llm_client)
