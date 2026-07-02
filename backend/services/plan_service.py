from graphs.plan_graph import (
    plan_graph
)
import uuid
from bson import ObjectId
from fastapi import HTTPException


async def create_plan(
        db,
        llm,
        journey_id,
        plan_days
):

    result = await plan_graph.ainvoke(
        {
            "db": db,
            "llm": llm,
            "journey_id": journey_id,
            "plan_days": plan_days
        } # type: ignore
    )

    return result["final_plan"]


async def get_plan(
        db,
        journey_id
):

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        }
    )

    if not journey:
        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    plan = journey.get("change_plan")

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found. Generate a plan first."
        )

    return normalize_plan(plan)


async def update_task_completion(
        db,
        journey_id,
        task_index,
        completed
):

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        }
    )

    if not journey:
        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    plan = journey.get("change_plan")

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found. Generate a plan first."
        )

    tasks = plan.get("tasks", [])

    if task_index < 0 or task_index >= len(tasks):
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    tasks[task_index]["completed"] = completed
    plan["tasks"] = tasks
    plan["total_tasks"] = len(tasks)
    plan["completed_tasks"] = sum(
        1
        for task in tasks
        if task.get("completed")
    )

    await db.aspirations.update_one(
        {
            "_id": ObjectId(journey_id)
        },
        {
            "$set": {
                "change_plan": plan
            }
        }
    )

    return normalize_plan(plan)


def normalize_plan(plan):
    tasks = []
    for task in plan.get("tasks", []):
        tasks.append({
            "task_id": task.get("task_id") or f"task_{uuid.uuid4().hex[:8]}",
            "replacement_count": task.get("replacement_count", 0),
            "history": task.get("history", []),
            **task,
            "completed": task.get("completed", False)
        })

    return {
        **plan,
        "tasks": tasks,
        "plan_days": plan.get("plan_days") or max(
            [
                task.get("day", 0)
                for task in tasks
            ]
            or [0]
        ),
        "total_tasks": len(tasks),
        "completed_tasks": sum(
            1
            for task in tasks
            if task.get("completed")
        )
    }
