from bson import ObjectId


async def save_gap_analysis_node(
        state
):

    db = state["db"]

    await db.user_journeys.update_one(
        {
            "_id": ObjectId(
                state["journey_id"]
            )
        },
        {
            "$set": {
                "gap_analysis":
                state["gap_analysis"]
            }
        }
    )

    return state