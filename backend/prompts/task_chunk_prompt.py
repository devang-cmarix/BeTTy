TASK_CHUNK_PROMPT = """
Generate daily coaching tasks.

Start Day:
{start_day}

End Day:
{end_day}

User Profile:
{profile}

Gap Analysis:
{gap_analysis}

Available Time Per Day:
{daily_commitment_minutes}

Available Time Windows:
{preferred_time_ranges}

User Notes:
{user_notes}

Rules:

1. Generate one task per day.

2. Task duration MUST NEVER exceed:
{daily_commitment_minutes}

3. Duration should be:
3 minutes up to daily_commitment_minutes.

4. scheduled_time MUST be inside one of:

{preferred_time_ranges}

5. Tasks should be:

- realistic
- simple
- actionable

6. Tasks must support:
- aspiration
- root causes
- obstacles
- mindset improvements

Learning Preferences:
{learning_preferences}

Allowed Resource Types:
{allowed_resource_types}

Resource Rules:

1. Only attach resource types listed in Allowed Resource Types.

2. If Allowed Resource Types contains "book":
You must include book resources across the plan.

3. If Allowed Resource Types contains "video":
You must include video resources across the plan.

4. If Allowed Resource Types contains "audio":
You must include audio resources across the plan.

5. If Allowed Resource Types is empty:
Every task must return resources as an empty list.

6. Resources must support the specific task.

7. Maximum:
0-2 resources per task.

8. Each resource must include:
- type: exactly one of "book", "video", "audio"
- title: the resource title
- url: a real public URL where the user can find the resource
- reason: why it supports this task

9. For books, use a reputable book page or search URL.

10. For videos, use a public video URL or search URL.

11. For audio, use a podcast/audio page or search URL.


Return structured output only.
"""
