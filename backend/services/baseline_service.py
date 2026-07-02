from bson import ObjectId

from services.scoring_service import (
    calculate_readiness_score
)

from utils.gap_analysis import (
    generate_gap_analysis
)


async def save_baseline(
        db,
        aspiration_id,
        baseline
):

    aspiration = await db.aspirations.find_one(
        {
            "_id": ObjectId(aspiration_id)
        }
    )

    if not aspiration:
        raise Exception(
            "Aspiration not found"
        )

    readiness = calculate_readiness_score(
        baseline["attitude_score"],
        baseline["effort_score"],
        baseline["motivation_score"]
    )

    gap_analysis = await generate_gap_analysis(
        aspiration["aspiration"]["text"],
        baseline,
        aspiration.get("input", {})
    )

    update = {
        "$set": {
            "baseline": baseline,
            "readiness": readiness,
            "gap_analysis": gap_analysis
        }
    }

    await db.aspirations.update_one(
        {
            "_id": ObjectId(aspiration_id)
        },
        update
    )

    return {
        "baseline": baseline,
        "readiness": readiness,
        "gap_analysis": gap_analysis
    }
