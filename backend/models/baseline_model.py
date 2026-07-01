from pydantic import BaseModel
from typing import List


class BaselineModel(BaseModel):

    attitude_score: int
    effort_score: int

    feelings: List[str]

    motivations: List[str]

    motivation_score: int

    values: List[str]

    age: int

    mindsets: List[str]

    obstacles: List[str]

    external_factors: List[str]

    daily_commitment_minutes: int

    preferred_time_ranges: List[dict]

    learning_preferences: List[str]

    notes: str = ""