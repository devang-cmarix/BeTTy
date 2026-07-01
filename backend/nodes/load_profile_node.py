from bson import ObjectId


async def load_profile_node(state):

    db = state["db"]

    profile = await db.user_journeys.find_one(
        {
            "_id": ObjectId(
                state["journey_id"]
            )
        }
    )

    state["profile"] = profile

    return state