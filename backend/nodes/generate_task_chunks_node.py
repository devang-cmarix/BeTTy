from langchain_core.prompts import (
    ChatPromptTemplate
)

from prompts.task_chunk_prompt import (
    TASK_CHUNK_PROMPT
)

from schemas.task_chunk_schema import (
    TaskChunk
)

from validators.task_validator import (
    validate_task_duration,
    validate_and_adjust_task_schedule
)

from utils.resource_helper import (
    get_allowed_resource_types,
    fetch_and_validate_resources
)

from utils.chunking import (
    build_chunks
)


async def generate_task_chunks_node(
        state
):

    profile = state["profile"]

    duration = state["plan_days"]

    chunks = build_chunks(
        duration
    )

    llm = (
        state["llm"]
        .with_structured_output(
            TaskChunk
        )
    )

    chain = (
        ChatPromptTemplate
        .from_template(
            TASK_CHUNK_PROMPT
        )
        | llm
    )

    tasks = []

    for start_day, end_day in chunks:

        baseline = profile["baseline"]
        learning_preferences = baseline.get(
            "learning_preferences",
            []
        )
        allowed_resource_types = get_allowed_resource_types(
            learning_preferences
        )
        chunk_days = end_day - start_day + 1

        result = await chain.ainvoke(
            {
                "start_day": start_day,

                "end_day": end_day,

                "chunk_days": chunk_days,

                "profile": profile,

                "gap_analysis":
                    state["gap_analysis"],

                "daily_commitment_minutes":
                    baseline[
                        "daily_commitment_minutes"
                    ],

                "preferred_time_ranges":
                    baseline.get(
                        "preferred_time_ranges",
                        []
                    ),

                "user_notes":
                    baseline.get(
                        "notes",
                        ""
                    ),
                "learning_preferences":
                    learning_preferences,

                "allowed_resource_types":
                    allowed_resource_types,
            }
        )

        if len(result.tasks) != chunk_days:
            raise ValueError(
                f"Expected {chunk_days} tasks for days {start_day}-{end_day}, "
                f"but LLM returned {len(result.tasks)} tasks."
            )

        chunk_tasks = [task.model_dump() for task in result.tasks]

        # Normalize day values so chunk tasks always cover the exact requested
        # day range, even if the LLM returns relative numbering or duplicates.
        for index, task in enumerate(chunk_tasks, start=0):
            task["day"] = start_day + index

        tasks.extend(chunk_tasks)

    tasks = validate_task_duration(
        tasks=tasks,
        max_minutes= baseline["daily_commitment_minutes"] # type: ignore
    )

    tasks = validate_and_adjust_task_schedule(
        tasks=tasks,
        preferred_time_ranges=baseline.get("preferred_time_ranges", [])
    )

    # Fetch and validate resources from real APIs concurrently
    import asyncio
    async def add_real_resources(t):
        baseline = profile["baseline"]
        learning_preferences = baseline.get("learning_preferences", [])
        allowed = get_allowed_resource_types(learning_preferences)
        # Detect if task is physical; if so, do not attach any resources
        text = " ".join(
            [
                str(t.get("title", "")),
                str(t.get("description", "")),
                str(t.get("rationale", "")),
            ]
        ).lower()

        physical_keywords = [
            "run",
            "walk",
            "jog",
            "lift",
            "squat",
            "press",
            "push",
            "pull",
            "stretch",
            "yoga",
            "exercise",
            "practice movement",
            "movement",
        ]

        if any(k in text for k in physical_keywords):
            t["resources"] = []
            return t

        # Only request audio/video when the task explicitly asks for listening/watching
        requires_audio = any(w in text for w in ("listen", "hear", "podcast", "audio"))
        requires_video = any(w in text for w in ("watch", "watching", "video", "youtube"))
        wants_reading = any(w in text for w in ("read", "book", "article", "chapter"))

        # Prioritize explicit task requests: if the task explicitly asks to
        # watch/listen/read, attempt to fetch those types even if not in the
        # user's learning_preferences. This ensures tasks that say "read" get
        # books/articles, and tasks that say "watch" get videos.
        filtered_allowed = []
        if requires_video:
            filtered_allowed.append("video")
        if requires_audio:
            filtered_allowed.append("audio")
        if wants_reading:
            filtered_allowed.extend(["book", "article"]) 
        # Ensure uniqueness
        filtered_allowed = list(dict.fromkeys(filtered_allowed))

        # If no filtered_allowed types, don't fetch any external resources
        if not filtered_allowed:
            t["resources"] = []
            return t

        max_seconds = None
        try:
            max_seconds = int(t.get("duration_minutes", 0)) * 60
            if max_seconds <= 0:
                max_seconds = None
        except Exception:
            max_seconds = None

        t["resources"] = await fetch_and_validate_resources(t["title"], filtered_allowed, max_duration_seconds=max_seconds)
        from utils.resource_helper import ensure_fallback_resources, update_task_with_real_resources
        t = ensure_fallback_resources(t)
        t = update_task_with_real_resources(t)
        return t

    tasks = list(await asyncio.gather(*(add_real_resources(t) for t in tasks)))

    state["task_chunks"] = tasks

    return state

