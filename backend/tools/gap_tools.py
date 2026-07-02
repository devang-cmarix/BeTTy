from bson import ObjectId


async def get_gap_analysis(
    db,
    journey_id: str
):
    """
    Fetch gap analysis.
    """

    journey = await db.aspirations.find_one(

        {

            "_id": ObjectId(journey_id)

        },

        {

            "gap_analysis": 1

        }

    )

    if journey is None:

        raise ValueError(
            "Journey not found."
        )

    gap = journey.get(
        "gap_analysis"
    )

    if not gap:

        return {

            "exists": False,

            "message": "Gap analysis has not been generated."

        }

    return {

        "exists": True,

        "gap_analysis": gap

    }


async def get_user_obstacles(
    db,
    journey_id: str
):

    result = await get_gap_analysis(
        db,
        journey_id
    )

    if not result["exists"]:

        return []

    return result[
        "gap_analysis"
    ].get(
        "my_obstacles",
        []
    )


async def get_success_criteria(
    db,
    journey_id: str
):

    result = await get_gap_analysis(
        db,
        journey_id
    )

    if not result["exists"]:

        return []

    return result[
        "gap_analysis"
    ].get(
        "my_success_criteria",
        []
    )


async def get_current_state(
    db,
    journey_id: str
):

    result = await get_gap_analysis(
        db,
        journey_id
    )

    if not result["exists"]:

        return None

    return result[
        "gap_analysis"
    ].get(
        "where_i_am"
    )


async def get_future_state(
    db,
    journey_id: str
):

    result = await get_gap_analysis(
        db,
        journey_id
    )

    if not result["exists"]:

        return None

    return result[
        "gap_analysis"
    ].get(
        "where_i_want_to_be"
    )