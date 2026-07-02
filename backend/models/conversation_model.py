from datetime import datetime

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):

    role: str

    content: str

    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )

    intent: dict | None = None

    tools: list[str] = []


class ConversationModel(BaseModel):

    journey_id: str

    messages: list[ConversationMessage] = []

    summary: str = ""

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )