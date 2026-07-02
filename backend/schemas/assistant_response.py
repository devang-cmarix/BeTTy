from pydantic import BaseModel
from typing import List


class Source(BaseModel):

    source_type: str

    source_name: str


class AssistantResponse(BaseModel):

    reply: str

    intent: str

    sources: List[Source] = []