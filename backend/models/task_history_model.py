from datetime import datetime

from pydantic import BaseModel, Field


class TaskHistoryModel(BaseModel):

    journey_id: str

    task_id: str

    day: int

    previous_title: str

    new_title: str

    reason: str

    replaced_at: datetime = Field(
        default_factory=datetime.utcnow
    )