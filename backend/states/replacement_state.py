from typing import TypedDict

class ReplacementState(TypedDict):

    db: object

    llm: object

    journey_id: str

    task_id: str

    alternative_id: str

    profile: dict

    aspiration: dict

    baseline: dict

    gap_analysis: dict

    complete_plan: dict

    current_task: dict

    previous_history: list

    alternatives: list

    updated_task: dict