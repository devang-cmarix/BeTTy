from pydantic import BaseModel
from typing import List

class AspirationRequest(BaseModel):
    force: str
    issue: str
    root_causes: List[str]

    emotion: str | None = None
    value: str | None = None
    mindset: str | None = None
    obstacle: str | None = None