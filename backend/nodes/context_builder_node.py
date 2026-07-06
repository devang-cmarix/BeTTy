import json


async def context_builder_node(state):

    results = state["tool_results"]

    sections = []

    # ---------------------------------
    # Query all completed plans for the user
    # ---------------------------------
    db = state["db"]
    active_id = state.get("journey_id")
    
    plans_section = []
    try:
        from bson import ObjectId
        cursor = db.aspirations.find({}, {"input": 1, "aspiration": 1, "baseline": 1, "change_plan": 1})
        count = 1
        async for doc in cursor:
            if not doc.get("baseline"):
                continue
            input_data = doc.get("input") or {}
            force = input_data.get("force")
            if not force and doc.get("change_plan"):
                force = doc["change_plan"].get("force")
            if not force:
                continue
                
            asp_text = ""
            asp_data = doc.get("aspiration")
            if asp_data:
                if isinstance(asp_data, dict):
                    asp_text = asp_data.get("text") or asp_data.get("aspiration") or ""
                else:
                    asp_text = str(asp_data)
            
            issue = input_data.get("issue") or "None"
            root_causes = input_data.get("root_causes") or []
            root_causes_str = ", ".join(root_causes) if isinstance(root_causes, list) else str(root_causes)
            
            is_active = str(doc["_id"]) == str(active_id)
            active_suffix = " (Active Plan)" if is_active else ""
            plans_section.append(
                f"{count}. {force}{active_suffix}\n"
                f"   Aspiration: {asp_text}\n"
                f"   Selected Issue: {issue}\n"
                f"   Root Causes: {root_causes_str}"
            )
            count += 1
    except Exception as e:
        pass
        
    if plans_section:
        plans_list_str = "\n".join(plans_section)
        sections.append(
            f"""
==========================
USER PLANS (ALL)
==========================
You currently have:
{plans_list_str}
"""
        )

    # ---------------------------------
    # Aspiration
    # ---------------------------------

    aspiration = results.get(
        "ASPIRATION_SHOW"
    )

    if aspiration and aspiration.get("exists"):
        aspiration_data = aspiration["aspiration"]
        input_data = aspiration.get("input") or {}
        force_label = input_data.get("force")
        issue = input_data.get("issue")
        root_causes = input_data.get("root_causes") or []

        sections.append(
            f"""
==========================
ASPIRATION & INITIAL INPUT
==========================
Aspiration text: {aspiration_data.get("text") if isinstance(aspiration_data, dict) else aspiration_data}
Life Force: {force_label}
Selected Issue: {issue}
Root Causes: {", ".join(root_causes) if isinstance(root_causes, list) else str(root_causes)}
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
        resources_list = task.get("resources", [])
        resources_text = ""
        if resources_list:
            resources_text = "\nResources:\n" + "\n".join([
                f"- [{res.get('type') or 'resource'}] {res.get('title')}: {res.get('url')} (Reason: {res.get('reason')})"
                for res in resources_list
            ])

        sections.append(

            f"""
==========================
TODAY'S TASK (Day {task.get("day")})
==========================

Day: {task.get("day")}

Title :

{task.get("title")}

Description :

{task.get("description")}

Goal :

{task.get("goal")}

Duration :

{task.get("duration_minutes")} minutes

Rationale :

{task.get("rationale")}{resources_text}
"""
        )

    # ---------------------------------
    # Task Show (Specific Day Task)
    # ---------------------------------

    task_show = results.get(
        "TASK_SHOW"
    )

    if task_show:
        resources_list = task_show.get("resources", [])
        resources_text = ""
        if resources_list:
            resources_text = "\nResources:\n" + "\n".join([
                f"- [{res.get('type') or 'resource'}] {res.get('title')}: {res.get('url')} (Reason: {res.get('reason')})"
                for res in resources_list
            ])

        sections.append(

            f"""
==========================
SPECIFIC DAY TASK (Day {task_show.get("day")})
==========================

Day: {task_show.get("day")}

Title:

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

{task_show.get("rationale")}{resources_text}
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
    # Task / Resource Search Results
    # ---------------------------------
    task_search = results.get("TASK_SEARCH")
    if task_search:
        search_lines = []
        for t in task_search:
            status = "Completed" if t.get("completed") else "Pending"
            resources_list = t.get("resources", [])
            resources_text = ""
            if resources_list:
                resources_text = "\n  Resources:\n" + "\n".join([
                    f"  - [{res.get('type') or 'resource'}] {res.get('title')}: {res.get('url')} (Reason: {res.get('reason')})"
                    for res in resources_list
                ])
            search_lines.append(
                f"- Day {t.get('day')}: {t.get('title')}\n  Description: {t.get('description')}\n  Details: {t.get('duration_minutes')} mins at {t.get('scheduled_time')}\n  Status: {status}{resources_text}"
            )
        search_text = "\n\n".join(search_lines)
        sections.append(
            f"""
==========================
TASK SEARCH RESULTS
==========================
Found the following matching tasks:
{search_text}
"""
        )

    resource_search = results.get("RESOURCE_SEARCH") or results.get("RESOURCE_SHOW")
    if resource_search:
        search_lines = []
        for t in resource_search:
            status = "Completed" if t.get("completed") else "Pending"
            resources_list = t.get("resources", [])
            resources_text = ""
            if resources_list:
                resources_text = "\n  Resources:\n" + "\n".join([
                    f"  - [{res.get('type') or 'resource'}] {res.get('title')}: {res.get('url')} (Reason: {res.get('reason')})"
                    for res in resources_list
                ])
            search_lines.append(
                f"- Day {t.get('day')}: {t.get('title')}\n  Description: {t.get('description')}\n  Details: {t.get('duration_minutes')} mins at {t.get('scheduled_time')}\n  Status: {status}{resources_text}"
            )
        search_text = "\n\n".join(search_lines)
        sections.append(
            f"""
==========================
RESOURCE SEARCH RESULTS
==========================
Found the following matching tasks/resources:
{search_text}
"""
        )

    # ---------------------------------

    state["formatted_context"] = "\n".join(
        sections
    )

    return state