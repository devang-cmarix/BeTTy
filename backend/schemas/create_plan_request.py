from pydantic import BaseModel


class CreatePlanRequest(
    BaseModel
):

    journey_id: str

    plan_days: int