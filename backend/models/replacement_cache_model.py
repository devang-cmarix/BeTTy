from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class ReplacementCacheModel(BaseModel):

    journey_id: str

    task_id: str

    alternatives: list

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    expireAt: datetime = Field(
        default_factory=lambda:
        datetime.utcnow() + timedelta(minutes=30)
    )