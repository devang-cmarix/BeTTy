from bson import ObjectId
from fastapi import HTTPException


async def create_gap_analysis(
        db,
        journey_id
):

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        }
    )

    if not journey:
        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    gap_analysis = journey.get("gap_analysis")

    if not gap_analysis:
        raise HTTPException(
            status_code=404,
            detail="Gap analysis not found. Save baseline first."
        )

    return gap_analysis
