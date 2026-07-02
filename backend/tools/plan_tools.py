from bson import ObjectId


async def get_plan(
    db,
    journey_id: str
) -> dict:
    """
    Returns the complete change plan.
    """

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        },
        {
            "change_plan": 1
        }
    )

    if journey is None:
        raise ValueError("Journey not found.")

    plan = journey.get("change_plan")

    if not plan:
        return {
            "exists": False,
            "message": "No plan has been generated yet."
        }

    return {
        "exists": True,
        "plan": plan
    }


async def get_plan_summary(
    db,
    journey_id: str
):

    result = await get_plan(
        db,
        journey_id
    )

    if not result["exists"]:
        return result

    plan = result["plan"]

    total = len(plan.get("tasks", []))

    completed = len([
        t
        for t in plan.get("tasks", [])
        if t.get("completed")
    ])

    pending = total - completed

    return {

        "total_days": plan.get("total_days"),

        "total_tasks": total,

        "completed_tasks": completed,

        "pending_tasks": pending,

        "completed_tasks_list": [
            {
                "day": t.get("day"),
                "title": t.get("title")
            }
            for t in plan.get("tasks", [])
            if t.get("completed")
        ]

    }


async def get_progress_percentage(
    db,
    journey_id: str
):

    summary = await get_plan_summary(
        db,
        journey_id
    )

    total = summary["total_tasks"]

    if total == 0:
        return 0

    return round(
        summary["completed_tasks"] * 100 / total,
        2
    )