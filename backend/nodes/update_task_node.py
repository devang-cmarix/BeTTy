from copy import deepcopy
from datetime import datetime

from schemas.task_plan_schema import ReplacementHistory


async def update_task_node(state):

    current_task = state["current_task"]

    cache = await state["db"].replacement_cache.find_one(

        {

            "journey_id": state["journey_id"],

            "task_id": state["task_id"]

        }

    )

    if cache is None:

        raise ValueError(
            "Replacement cache expired."
        )

    selected_task = None

    for task in cache["alternatives"]:

        if task["alternative_id"] == state["alternative_id"]:

            selected_task = task

            break

    if selected_task is None:

        raise ValueError(
            "Alternative not found."
        )

    # -----------------------------
    # Save existing task in history
    # -----------------------------

    history_item = ReplacementHistory(

        title=current_task["title"],

        description=current_task["description"],

        rationale=current_task["rationale"],

        replaced_at=datetime.utcnow()

    )

    history = current_task.get("history", [])

    history.append(history_item.model_dump())

    # -----------------------------
    # Preserve immutable fields
    # -----------------------------

    updated_task = deepcopy(current_task)

    updated_task["title"] = selected_task["title"]

    updated_task["description"] = selected_task["description"]

    updated_task["goal"] = selected_task["goal"]

    updated_task["scheduled_time"] = selected_task["scheduled_time"]

    updated_task["duration_minutes"] = selected_task["duration_minutes"]

    updated_task["rationale"] = selected_task["rationale"]

    updated_task["resources"] = selected_task["resources"]

    updated_task["history"] = history

    updated_task["replacement_count"] += 1

    updated_task["status"] = "pending"

    updated_task["completed"] = False

    state["updated_task"] = updated_task

    return state