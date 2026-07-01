from bson import ObjectId


async def save_plan_node(state):

    db = state["db"]

    await db.aspirations.update_one(
        {
            "_id": ObjectId(
                state["journey_id"]
            )
        },
        {
            "$set": {
                "change_plan":
                    state["final_plan"]
            }
        }
    )

    return state
