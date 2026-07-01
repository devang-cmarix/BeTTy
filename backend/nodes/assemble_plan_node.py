import uuid

async def assemble_plan_node(
        state
):
    tasks = [
        {
            "task_id": task.get("task_id") or f"task_{uuid.uuid4().hex[:8]}",
            "replacement_count": task.get("replacement_count", 0),
            "history": task.get("history", []),
            **task,
            "completed": task.get(
                "completed",
                False
            )
        }
        for task in state["task_chunks"]
    ]

    state["final_plan"] = {

        "total_tasks":
            len(
                tasks
            ),

        "completed_tasks": 0,

        "plan_days":
            state["plan_days"],

        "tasks":
            tasks,

    }

    return state
