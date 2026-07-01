from fastapi import (
    APIRouter,
    Depends
)
from pydantic import BaseModel

from database.mongodb import (
    get_db
)

from services.plan_service import (
    create_plan,
    get_plan,
    update_task_completion
)

from schemas.create_plan_request import (
    CreatePlanRequest
)

from llm_config import llm

router = APIRouter(
    prefix="/plan",
    tags=["Plan"]
)


class TaskCompletionRequest(BaseModel):
    completed: bool

@router.post("/generate")
async def generate_plan(
    request: CreatePlanRequest,
    db=Depends(get_db)
):

    result = await create_plan(
        db=db,
        llm=llm,
        journey_id=request.journey_id,
        plan_days=request.plan_days
    )

    return {
        "success": True,
        "data": result
    }


@router.get("/{journey_id}")
async def read_plan(
    journey_id: str,
    db=Depends(get_db)
):

    result = await get_plan(
        db=db,
        journey_id=journey_id
    )

    return {
        "success": True,
        "data": result
    }


@router.patch("/{journey_id}/tasks/{task_index}")
async def complete_task(
    journey_id: str,
    task_index: int,
    request: TaskCompletionRequest,
    db=Depends(get_db)
):

    result = await update_task_completion(
        db=db,
        journey_id=journey_id,
        task_index=task_index,
        completed=request.completed
    )

    return {
        "success": True,
        "data": result
    }
