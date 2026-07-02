from bson import ObjectId


async def get_aspiration(
    db,
    journey_id: str
) -> dict:
    """
    Fetch the user's aspiration from MongoDB.
    """

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        },
        {
            "aspiration": 1
        }
    )

    if journey is None:
        raise ValueError("Journey not found.")

    aspiration = journey.get("aspiration")

    if not aspiration:
        return {
            "exists": False,
            "message": "Aspiration has not been created yet."
        }

    return {
        "exists": True,
        "aspiration": aspiration
    }


async def aspiration_exists(
    db,
    journey_id: str
) -> bool:

    count = await db.aspirations.count_documents(
        {
            "_id": ObjectId(journey_id),
            "aspiration": {
                "$exists": True
            }
        }
    )

    return count > 0