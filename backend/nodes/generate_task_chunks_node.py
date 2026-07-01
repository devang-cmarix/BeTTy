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
    validate_task_duration
)

from utils.chunking import (
    build_chunks
)


def get_allowed_resource_types(
        learning_preferences
):
    allowed = []

    for preference in learning_preferences:
        normalized = preference.lower()

        if "reading" in normalized:
            allowed.append("book")

        if "video" in normalized or "watching" in normalized:
            allowed.append("video")

        if "audio" in normalized or "podcast" in normalized or "listening" in normalized:
            allowed.append("audio")

    return list(dict.fromkeys(allowed))


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

        result = await chain.ainvoke(
            {
                "start_day": start_day,

                "end_day": end_day,

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

        tasks.extend(
            [
                task.model_dump()
                for task in result.tasks
            ]
        )

    tasks = validate_task_duration(
        tasks=tasks,
        max_minutes=
            baseline[
                "daily_commitment_minutes"
            ]
    )

    state["task_chunks"] = tasks

    return state
