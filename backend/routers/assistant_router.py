from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from motor.motor_asyncio import AsyncIOMotorDatabase

from database.mongodb import (
    get_db
)

from llm_config import (
    llm
)

from schemas.assistant_request import (
    AssistantRequest
)

from services.supervisor_service import (
    SupervisorService
)

router = APIRouter(

    prefix="/assistant",

    tags=["AI Coach"]

)


from datetime import datetime
from bson import ObjectId

def serialize_for_json(data):
    if isinstance(data, dict):
        return {k: serialize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_for_json(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    return data


@router.post("")

async def chat(

    request: AssistantRequest,

    db: AsyncIOMotorDatabase = Depends(
        get_db
    )

):

    try:

        service = SupervisorService(

            db=db,

            llm=llm

        )

        result = await service.chat(

            journey_id=request.journey_id,

            message=request.message,

            history=[

                h.model_dump()

                for h in request.history

            ]

        )

        return {

            "success": True,

            "reply": result["reply"],

            "intent": result["intent"],

            "sources": serialize_for_json(result["sources"]),

            "suggestions": result.get("suggestions", [])

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )