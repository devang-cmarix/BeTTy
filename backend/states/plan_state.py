from typing import TypedDict


class PlanState(TypedDict):

    db: object

    llm: object

    journey_id: str

    plan_days: int

    profile: dict

    gap_analysis: dict

    task_chunks: list

    resources: dict

    final_plan: dict
