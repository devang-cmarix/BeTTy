from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from database.mongodb import get_db
from schemas.aspiration import AspirationRequest
from services.aspiration_service import (
    generate_aspiration
)

router = APIRouter(
    tags=["Aspiration"]
)


@router.post("/generate-aspiration")
async def aspiration(
    request: AspirationRequest,
    db=Depends(get_db)
):

    result = generate_aspiration(
        request
    )

    document = {
        "input": request.model_dump(),
        "aspiration": {
            "text": result
        },
        "created_at": datetime.now(timezone.utc)
    }

    inserted = await db.aspirations.insert_one(document)

    return {
        "aspiration_id": str(inserted.inserted_id),
        "aspiration": result
    }
