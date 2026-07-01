from pydantic import BaseModel
from typing import List


class ResourceItem(BaseModel):

    type: str

    title: str

    url: str

    reason: str


class DailyTask(BaseModel):

    day: int

    title: str

    description: str

    scheduled_time: str

    duration_minutes: int

    rationale: str

    resources: List[ResourceItem]


class TaskChunk(BaseModel):

    tasks: List[DailyTask]
