from bson import ObjectId

from models.task_history_model import (
    TaskHistoryModel
)


async def save_task_history_node(state):

    db = state["db"]

    journey = state["profile"]

    updated_task = state["updated_task"]

    current_task = state["current_task"]

    # -----------------------------------
    # Update task inside task_plan
    # -----------------------------------

    tasks = journey["change_plan"]["tasks"]

    for index, task in enumerate(tasks):

        if task["task_id"] == updated_task["task_id"]:

            tasks[index] = updated_task

            break

    await db.aspirations.update_one(

        {

            "_id": ObjectId(state["journey_id"])

        },

        {

            "$set": {

                "change_plan.tasks": tasks

            }

        }

    )

    # -----------------------------------
    # Save replacement history
    # -----------------------------------

    history = TaskHistoryModel(

        journey_id=state["journey_id"],

        task_id=updated_task["task_id"],

        day=updated_task["day"],

        previous_title=current_task["title"],

        new_title=updated_task["title"],

        reason="User requested replacement"

    )

    await db.task_history.insert_one(

        history.model_dump()

    )

    await db.replacement_cache.delete_one(

        {

            "journey_id": state["journey_id"],

            "task_id": state["task_id"]

        }

    )

    return state