from schemas.task_plan_schema import DailyTask


def validate_task(task: DailyTask):

    if task.day <= 0:
        raise ValueError(
            "Day must be greater than zero."
        )

    if task.duration_minutes <= 0:
        raise ValueError(
            "Duration must be greater than zero."
        )

    if not task.title.strip():
        raise ValueError(
            "Task title cannot be empty."
        )

    if not task.goal.strip():
        raise ValueError(
            "Task goal cannot be empty."
        )

    return True


def validate_task_duration(tasks: list, max_minutes: int) -> list:
    for task in tasks:
        if task.get("duration_minutes", 0) > max_minutes:
            task["duration_minutes"] = max_minutes
    return tasks