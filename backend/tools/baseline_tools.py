from bson import ObjectId


async def get_baseline(
    db,
    journey_id: str
) -> dict:
    """
    Fetch baseline assessment.
    """

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        },
        {
            "baseline": 1
        }
    )

    if journey is None:
        raise ValueError("Journey not found.")

    baseline = journey.get("baseline")

    if not baseline:

        return {

            "exists": False,

            "message": "Baseline assessment not completed."

        }

    return {

        "exists": True,

        "baseline": baseline

    }


async def get_daily_commitment(
    db,
    journey_id: str
):

    journey = await db.aspirations.find_one(

        {
            "_id": ObjectId(journey_id)
        },

        {
            "baseline.daily_commitment_minutes": 1
        }

    )

    if not journey:

        return None

    baseline = journey.get(
        "baseline",
        {}
    )

    return baseline.get(
        "daily_commitment_minutes"
    )


async def get_user_motivation(
    db,
    journey_id: str
):

    journey = await db.aspirations.find_one(

        {
            "_id": ObjectId(journey_id)
        },

        {
            "baseline.motivation_score": 1
        }

    )

    if not journey:

        return None

    baseline = journey.get(
        "baseline",
        {}
    )

    return baseline.get(
        "motivation_score"
    )