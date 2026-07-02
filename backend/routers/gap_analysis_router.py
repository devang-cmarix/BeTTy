from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from database.mongodb import get_db
from services.gap_analysis_service import (
    create_gap_analysis
)

router = APIRouter()

class GapAnalysisUpdatePayload(BaseModel):
    my_success_criteria: list[str]

@router.post(
    "/gap-analysis/{journey_id}"
)
async def generate_gap_analysis(
        journey_id: str,
        db=Depends(get_db)
):

    result = await create_gap_analysis(
        db,
        journey_id
    )

    return result


@router.patch("/gap-analysis/{journey_id}")
async def update_gap_analysis(
    journey_id: str,
    payload: GapAnalysisUpdatePayload,
    db=Depends(get_db)
):
    from bson import ObjectId
    from fastapi import HTTPException
    
    journey = await db.aspirations.find_one({"_id": ObjectId(journey_id)})
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
        
    gap_analysis = journey.get("gap_analysis", {})
    gap_analysis["my_success_criteria"] = payload.my_success_criteria
    gap_analysis["success_criteria"] = payload.my_success_criteria
    
    await db.aspirations.update_one(
        {"_id": ObjectId(journey_id)},
        {"$set": {"gap_analysis": gap_analysis}}
    )
    return {"success": True, "gap_analysis": gap_analysis}

