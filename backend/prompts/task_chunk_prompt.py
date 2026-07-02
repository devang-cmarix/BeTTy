TASK_CHUNK_PROMPT = """
Generate daily coaching tasks.

Start Day:
{start_day}

End Day:
{end_day}

Total Days in this chunk:
{chunk_days}

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

1. Generate exactly {chunk_days} tasks: one task for each day from {start_day} to {end_day} inclusive.

2. Task duration (duration_minutes) MUST be planned according to the user input in the baseline:
- If the baseline daily commitment is 50 minutes, the task duration should be in the range of 40-50 minutes.
- If the baseline daily commitment is 40 minutes, you MUST vary the task durations: include a mix of full-length tasks (40 minutes) and shorter tasks (e.g., 15, 20, 25, or 30 minutes) across the days. Do NOT make every task 40 minutes.
- Otherwise, it should be exactly or very close to {daily_commitment_minutes} minutes.

3. scheduled_time MUST be planned such that the entire task (start time + duration) fits COMPLETELY within one of the preferred time ranges: {preferred_time_ranges}. The task CANNOT start at the end of the range or overflow past it. For example, if a preferred time range is 13:56 to 17:00, and the task duration is 40 minutes, the task start time must be at or before 16:20 so that it finishes by 17:00 (Task Start Time + Task Duration <= Time Range End Time).

5. Tasks should be:

- realistic
- simple
- actionable
- DO NOT instruct the user to search for, find, pick, or choose resources (e.g. do not write descriptions like 'Find a podcast...' or 'Search for an article...'). Assume the resources will be directly supplied. Frame the task as consuming/learning from the attached resource.

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

1. Only attach resource types listed in Allowed Resource Types when they are
	relevant to the individual task (do NOT attach every allowed type to every
	day).

2. Include a resource of type "audio"/"podcast" only when the task text
	explicitly suggests listening (words like "listen", "hear", "podcast",
	or "audio"). Do not add audio just because "audio" is an allowed type.

3. Include a resource of type "video" only when the task text explicitly
	suggests watching (words like "watch", "video", "youtube") or when a
	short instructional video clearly supports the task.

4. Include a resource of type "book" or "article" only when the task text
	explicitly suggests reading (words like "read", "book", "chapter",
	"article", "ebook"). Do not add reading resources to a task that is only
	about watching or listening.

5. If the task text explicitly asks to read a book, article, or chapter,
	use only reading resources for that task, not audio or video.

6. If the task text explicitly asks to watch a video or use YouTube,
	use only video resources for that task.

7. If a task is a physical/movement activity (e.g. contains words like
	"run", "walk", "lift", "squat", "practice movement", "exercise",
	"stretch", "yoga"), DO NOT attach any audio, video, book, or article
	resources for that task — the task should be purely action-oriented.

8. If Allowed Resource Types is empty, every task must return resources as an
	empty list.

9. If the user prefers watching videos, include at least one video-based task
	per 15-day period when it naturally fits the plan.

10. If the user prefers listening, include at least one audio-based task per
	15-day period when it naturally fits the plan.

11. If the user prefers reading, include at least one book/article-based task
	per 15-day period when it naturally fits the plan.


6. Resources must directly support the specific task and should fit within
	the task's duration.

7. Maximum: 0-2 resources per task.

8. Each resource must include:
	- type: exactly one of "book", "video", "audio"
	- title: the resource title
	- url: a real public URL where the user can find the resource
	- reason: why it supports this task

9. For books, use a reputable book page or search URL.

10. For videos, use a public video URL or search URL (prefer YouTube when the
	 user indicated video/YouTube preference).

11. For audio, use a podcast/audio page or search URL.

Return structured output only.
"""
