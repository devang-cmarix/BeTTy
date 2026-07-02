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

    keyword = keyword.lower()

    tasks = await get_all_tasks(
        db,
        journey_id
    )

    results = []

    for task in tasks:

        if (

            keyword in task["title"].lower()

            or

            keyword in task["description"].lower()

        ):

            results.append(task)

    return results