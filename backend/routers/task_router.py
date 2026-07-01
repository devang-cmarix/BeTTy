from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.mongodb import get_db

from llm_config import get_llm

from schemas.replace_task_request import (
    ReplaceTaskRequest
)

from services.replacement_service import (
    ReplacementService
)

router = APIRouter(
    prefix="/tasks",
    tags=["Task Replacement"]
)


# ---------------------------------------------------
# Generate Alternatives
# ---------------------------------------------------

@router.post(
    "/{journey_id}/{task_id}/alternatives"
)
async def generate_task_alternatives(

    journey_id: str,

    task_id: str,

    db: AsyncIOMotorDatabase = Depends(
        get_db
    )

):

    try:

        llm = get_llm()

        service = ReplacementService(
            db=db,
            llm=llm
        )

        alternatives = await service.generate_alternatives(

            journey_id=journey_id,

            task_id=task_id

        )

        return {

            "success": True,

            "message": "Alternatives generated successfully.",

            "alternatives": alternatives

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ---------------------------------------------------
# Apply Selected Alternative
# ---------------------------------------------------

@router.patch(
    "/{journey_id}/{task_id}/replace"
)
async def replace_task(

    journey_id: str,

    task_id: str,

    request: ReplaceTaskRequest,

    db: AsyncIOMotorDatabase = Depends(
        get_db
    )

):

    try:

        llm = get_llm()

        service = ReplacementService(
            db=db,
            llm=llm
        )

        updated_task = await service.apply_replacement(

            journey_id=journey_id,

            task_id=task_id,

            alternative_id=request.alternative_id

        )

        return {

            "success": True,

            "message": "Task replaced successfully.",

            "task": updated_task

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )