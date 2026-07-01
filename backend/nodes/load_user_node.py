from bson import ObjectId
from fastapi import HTTPException


async def load_user_node(state):

    db = state["db"]

    doc = await db.aspirations.find_one(
        {
            "_id": ObjectId(
                state["journey_id"]
            )
        }
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    if "baseline" not in doc or "gap_analysis" not in doc:
        raise HTTPException(
            status_code=400,
            detail="Save baseline and gap analysis before generating a plan"
        )

    state["profile"] = doc
    state["gap_analysis"] = doc["gap_analysis"]

    return state
