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
        dur = task.get("duration_minutes", 0)
        if max_minutes == 50:
            if dur < 40:
                task["duration_minutes"] = 40
            elif dur > 50:
                task["duration_minutes"] = 50
        elif max_minutes == 40:
            if dur < 15:
                task["duration_minutes"] = 15
            elif dur > 40:
                task["duration_minutes"] = 40
        else:
            if dur > max_minutes:
                task["duration_minutes"] = max_minutes
    return tasks


def time_to_minutes(t_str: str) -> int:
    try:
        h, m = map(int, t_str.split(':'))
        return h * 60 + m
    except Exception:
        return 0


def minutes_to_time(m: int) -> str:
    h = (m // 60) % 24
    min = m % 60
    return f"{h:02d}:{min:02d}"


def circular_distance(m1: int, m2: int) -> int:
    diff = abs(m1 - m2) % 1440
    return min(diff, 1440 - diff)


def validate_and_adjust_task_schedule(tasks: list, preferred_time_ranges: list) -> list:
    if not preferred_time_ranges:
        return tasks

    for task in tasks:
        duration = task.get("duration_minutes", 0)
        scheduled_str = task.get("scheduled_time", "")
        if not scheduled_str:
            continue

        task_start = time_to_minutes(scheduled_str)

        best_range = None
        best_shift = None
        min_dist = float('inf')

        for r in preferred_time_ranges:
            start_str = r.get("start", "")
            end_str = r.get("end", "")
            if not start_str or not end_str:
                continue

            r_start = time_to_minutes(start_str)
            r_end = time_to_minutes(end_str)

            # Handle midnight crossing range length
            r_len = (r_end - r_start) % 1440
            if r_len == 0 and r_start == r_end:
                r_len = 1440

            # If the task duration is larger than the range length, cap task duration
            effective_duration = min(duration, r_len)

            # Start offset relative to range start
            diff = (task_start - r_start) % 1440

            # Valid start interval relative to r_start is [0, r_len - effective_duration]
            L = r_len - effective_duration

            if diff <= L:
                # Task already fits in this range with 0 distance/shift
                best_range = r
                best_shift = task_start
                min_dist = 0
                break
            else:
                # It does not fit. Compute distance to the valid start range
                # The valid start interval has two boundaries relative to r_start: 0 and L
                # Corresponding absolute times: r_start and (r_start + L) % 1440
                dist_to_start = circular_distance(task_start, r_start)
                dist_to_end = circular_distance(task_start, (r_start + L) % 1440)

                if dist_to_start < dist_to_end:
                    curr_dist = dist_to_start
                    curr_shift = r_start
                else:
                    curr_dist = dist_to_end
                    curr_shift = (r_start + L) % 1440

                if curr_dist < min_dist:
                    min_dist = curr_dist
                    best_range = r
                    best_shift = curr_shift

        if best_shift is not None:
            # Apply the schedule adjustment
            task["scheduled_time"] = minutes_to_time(best_shift)
            # If the duration was capped to range length, update it
            if best_range:
                r_start = time_to_minutes(best_range.get("start", ""))
                r_end = time_to_minutes(best_range.get("end", ""))
                r_len = (r_end - r_start) % 1440
                if r_len == 0 and r_start == r_end:
                    r_len = 1440
                if duration > r_len:
                    task["duration_minutes"] = r_len

    return tasks