from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field

from schemas.task_plan_schema import Resource


class ReplacementTask(BaseModel):

    alternative_id: str = Field(
        default_factory=lambda: f"alt_{uuid4().hex[:8]}"
    )

    activity_type: str

    title: str

    description: str

    goal: str

    scheduled_time: str

    duration_minutes: int

    rationale: str

    resources: List[Resource]


class ReplacementResponse(BaseModel):

    alternatives: List[ReplacementTask]