from typing import Literal

from pydantic import BaseModel


class IntentSchema(BaseModel):

    domain: Literal[
        "ASPIRATION",
        "BASELINE",
        "GAP_ANALYSIS",
        "PLAN",
        "TASK",
        "RESOURCE",
        "HISTORY",
        "GENERAL"
    ]

    action: Literal[
        "SHOW",
        "TODAY",
        "NEXT",
        "COMPLETE",
        "SKIP",
        "REPLACE",
        "PROGRESS",
        "EXPLAIN",
        "SEARCH",
        "CHAT"
    ]

    confidence: float
    
    day: int | None = None
    keyword: str | None = None
    task_id: str | None = None