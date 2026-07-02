from pydantic import BaseModel
from typing import Optional


class ChatHistory(BaseModel):

    role: str

    content: str


class AssistantRequest(BaseModel):

    journey_id: Optional[str] = None

    message: str

    history: list[ChatHistory] = []