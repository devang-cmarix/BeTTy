from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ----------------------------
# Resources
# ----------------------------

class Resource(BaseModel):

    resource_type: str
    title: str
    author: Optional[str] = None
    url: Optional[str] = None


# ----------------------------
# Replacement History
# ----------------------------

class ReplacementHistory(BaseModel):

    title: str

    description: str

    rationale: str

    replaced_at: datetime = Field(
        default_factory=datetime.utcnow
    )


# ----------------------------
# Daily Task
# ----------------------------

class DailyTask(BaseModel):

    task_id: str

    day: int

    goal: str

    title: str

    description: str

    scheduled_time: str

    duration_minutes: int

    rationale: str

    resources: List[Resource] = []

    status: str = "pending"

    completed: bool = False

    replacement_count: int = 0

    history: List[ReplacementHistory] = []


# ----------------------------
# Complete Plan
# ----------------------------

class TaskPlan(BaseModel):

    total_days: int

    total_tasks: int

    tasks: List[DailyTask]

    books: List[Resource] = []

    videos: List[Resource] = []

    audios: List[Resource] = []