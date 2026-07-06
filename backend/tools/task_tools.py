from bson import ObjectId


async def get_all_tasks(
    db,
    journey_id: str
):

    journey = await db.aspirations.find_one(
        {
            "_id": ObjectId(journey_id)
        },
        {
            "change_plan.tasks": 1
        }
    )

    if journey is None:
        raise ValueError("Journey not found.")

    return journey.get(
        "change_plan",
        {}
    ).get(
        "tasks",
        []
    )


async def get_task_by_day(
    db,
    journey_id: str,
    day: int = None
):

    tasks = await get_all_tasks(
        db,
        journey_id
    )

    if day is None:
        # Fall back to finding the first incomplete task
        for task in tasks:
            if not task.get("completed"):
                return task
        if tasks:
            return tasks[-1]
        return None

    for task in tasks:

        if task["day"] == day:
            return task

    return None


async def get_task_by_id(
    db,
    journey_id: str,
    task_id: str
):

    tasks = await get_all_tasks(
        db,
        journey_id
    )

    for task in tasks:

        if task["task_id"] == task_id:
            return task

    return None


async def get_today_task(
    db,
    journey_id: str,
    day: int = None
):
    """
    Your frontend or backend passes today's plan day.
    """

    return await get_task_by_day(
        db,
        journey_id,
        day
    )


async def get_completed_tasks(
    db,
    journey_id: str
):

    tasks = await get_all_tasks(
        db,
        journey_id
    )

    return [

        task

        for task in tasks

        if task.get("completed")

    ]


async def get_pending_tasks(
    db,
    journey_id: str
):

    tasks = await get_all_tasks(
        db,
        journey_id
    )

    return [

        task

        for task in tasks

        if not task.get("completed")

    ]


async def search_tasks(
    db,
    journey_id: str,
    keyword: str
):

    if not keyword:
        return []

    keyword = str(keyword).lower()

    tasks = await get_all_tasks(
        db,
        journey_id
    )

    results = []

    for task in tasks:
        task_title = task.get("title", "").lower()
        task_desc = task.get("description", "").lower()

        is_match = False
        if (
            keyword in task_title
            or task_title in keyword
            or keyword in task_desc
            or task_desc in keyword
        ):
            is_match = True

        if not is_match:
            # Search within task resources
            for res in task.get("resources", []):
                res_title = res.get("title", "").lower()
                res_url = res.get("url", "").lower()
                res_reason = res.get("reason", "").lower()
                if (
                    (res_title and (keyword in res_title or res_title in keyword))
                    or (res_url and (keyword in res_url or res_url in keyword))
                    or (res_reason and (keyword in res_reason or res_reason in keyword))
                ):
                    is_match = True
                    break

        if is_match:
            results.append(task)

    return results