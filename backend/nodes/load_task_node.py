from bson import ObjectId


async def load_task_node(state):

    db = state["db"]

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(state["journey_id"])
        }
    )

    if journey is None:
        raise ValueError("Journey not found.")

    task_plan = journey.get("change_plan")

    if task_plan is None:
        raise ValueError("Task plan not found.")

    current_task = None

    for task in task_plan["tasks"]:

        if task["task_id"] == state["task_id"]:

            current_task = task

            break

    if current_task is None:
        raise ValueError("Task not found.")

    state["profile"] = journey

    state["complete_plan"] = task_plan

    state["current_task"] = current_task

    state["previous_history"] = current_task.get(
        "history",
        []
    )

    return state