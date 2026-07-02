from schemas.intent_schema import IntentSchema
from typing import TypedDict

class SupervisorState(TypedDict):

    db: object

    llm: object

    journey_id: str

    user_message: str

    history: list

    intent: IntentSchema

    tool_plan: list

    tool_results: dict

    retrieved_context: dict

    response: str

    response_sources: list

    day: int | None

    keyword: str | None

    task_id: str | None
    
    formatted_context: str
    
    conversation_summary: str