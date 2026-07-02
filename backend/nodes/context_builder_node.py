import json


async def context_builder_node(state):

    results = state["tool_results"]

    sections = []

    # ---------------------------------
    # Aspiration
    # ---------------------------------

    aspiration = results.get(
        "ASPIRATION_SHOW"
    )

    if aspiration and aspiration.get("exists"):

        sections.append(

            f"""
==========================
ASPIRATION
==========================

{json.dumps(
    aspiration["aspiration"],
    indent=2,
    ensure_ascii=False
)}
"""
        )

    # ---------------------------------
    # Baseline
    # ---------------------------------

    baseline = results.get(
        "BASELINE_SHOW"
    )

    if baseline and baseline.get("exists"):

        sections.append(

            f"""
==========================
BASELINE
==========================

{json.dumps(
    baseline["baseline"],
    indent=2,
    ensure_ascii=False
)}
"""
        )

    # ---------------------------------
    # Gap Analysis
    # ---------------------------------

    gap = results.get(
        "GAP_ANALYSIS_SHOW"
    )

    if gap and gap.get("exists"):

        sections.append(

            f"""
==========================
GAP ANALYSIS
==========================

{json.dumps(
    gap["gap_analysis"],
    indent=2,
    ensure_ascii=False
)}
"""
        )

    # ---------------------------------
    # Plan
    # ---------------------------------

    plan = results.get(
        "PLAN_SHOW"
    )

    if plan and plan.get("exists"):

        plan_data = plan["plan"]
        tasks_list = plan_data.get("tasks", [])

        tasks_summary = []
        for t in tasks_list:
            status = "Completed" if t.get("completed") else "Pending"
            tasks_summary.append(
                f"- Day {t.get('day')}: {t.get('title')} ({t.get('duration_minutes')} mins at {t.get('scheduled_time')}) - {status}"
            )
        tasks_text = "\n".join(tasks_summary)
        duration_val = plan_data.get("total_days") or plan_data.get("plan_days") or len(tasks_list)

        sections.append(

            f"""
==========================
CHANGE PLAN
==========================

Duration : {duration_val} days
Total Tasks : {len(tasks_list)}

Tasks list:
{tasks_text}
"""
        )

    # ---------------------------------
    # Progress
    # ---------------------------------

    progress = results.get(
        "PLAN_PROGRESS"
    )

    if progress:
        completed = progress.get("completed_tasks", 0)
        pending = progress.get("pending_tasks", 0)
        total = progress.get("total_tasks") or (completed + pending)
        percentage = round(completed * 100 / total, 2) if total > 0 else 0

        completed_list = progress.get("completed_tasks_list", [])
        if completed_list:
            completed_text = "\n".join([
                f"- Day {t.get('day')}: {t.get('title')}"
                for t in completed_list
            ])
        else:
            completed_text = "None"

        sections.append(

            f"""
==========================
PROGRESS
==========================

Completed Tasks Count : {completed}
Pending Tasks Count : {pending}
Total Tasks Count : {total}
Progress : {percentage}%

Completed Tasks Names:
{completed_text}
"""
        )

    # ---------------------------------
    # Today's Task
    # ---------------------------------

    task = results.get(
        "TASK_TODAY"
    )

    if task:

        sections.append(

            f"""
==========================
TODAY'S TASK
==========================

Title :

{task.get("title")}

Description :

{task.get("description")}

Goal :

{task.get("goal")}

Duration :

{task.get("duration_minutes")} minutes

Rationale :

{task.get("rationale")}
"""
        )

    # ---------------------------------
    # Task Show (Specific Day Task)
    # ---------------------------------

    task_show = results.get(
        "TASK_SHOW"
    )

    if task_show:

        sections.append(

            f"""
==========================
SPECIFIC DAY TASK
==========================

Title :

{task_show.get("title")}

Description :

{task_show.get("description")}

Goal :

{task_show.get("goal")}

Duration :

{task_show.get("duration_minutes")} minutes

Scheduled Time :

{task_show.get("scheduled_time")}

Completed :

{task_show.get("completed")}

Rationale :

{task_show.get("rationale")}
"""
        )

    # ---------------------------------
    # History
    # ---------------------------------

    history = results.get(
        "HISTORY_SHOW"
    )

    if history:
        from datetime import datetime
        history_lines = []
        for h in history:
            replaced_time = h.get("replaced_at")
            if isinstance(replaced_time, datetime):
                time_str = replaced_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = str(replaced_time)
            history_lines.append(
                f"- Day {h.get('day')}: Replaced '{h.get('previous_title')}' with '{h.get('new_title')}' (Reason: {h.get('reason')}) at {time_str}"
            )
        history_text = "\n".join(history_lines)

        sections.append(

            f"""
==========================
TASK HISTORY
==========================

{history_text}
"""
        )

    # ---------------------------------

    state["formatted_context"] = "\n".join(
        sections
    )

    return state