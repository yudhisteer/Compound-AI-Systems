import typing as t

from fastapi import APIRouter

from core.llm.llm_service import llm_service_factory

predict_router = r = APIRouter()

llm_service = llm_service_factory()


@r.post("/chat/llm", response_model=t.Dict)
async def think() -> t.Dict:
    predict_response = llm_service.predict("Hello, how are you?")
    embedding_response = llm_service.get_embeddings("Hello, how are you?")
    # return predict_response

    return {"message": "Hello, how are you?", "response": embedding_response}
