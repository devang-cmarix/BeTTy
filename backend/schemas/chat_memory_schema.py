from pydantic import BaseModel

from models.conversation_model import (
    ConversationMessage
)


class ChatMemorySchema(BaseModel):

    journey_id: str

    messages: list[ConversationMessage]

    summary: str = ""