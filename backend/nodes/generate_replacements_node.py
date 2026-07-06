from langchain_core.prompts import ChatPromptTemplate

from prompts.replacement_prompt import (
    REPLACEMENT_PROMPT
)

from schemas.replacement_schema import (
    ReplacementResponse
)

from datetime import datetime
from datetime import timedelta

async def generate_replacements_node(
        state
):

    llm = state["llm"]

    structured_llm = llm.with_structured_output(
        ReplacementResponse
    )

    prompt = ChatPromptTemplate.from_template(
        REPLACEMENT_PROMPT
    )

    chain = prompt | structured_llm

    result = await chain.ainvoke(

        {

            "aspiration":
            state["aspiration"],

            "baseline":
            state["baseline"],

            "gap_analysis":
            state["gap_analysis"],

            "plan":
            state["complete_plan"],

            "current_task":
            state["current_task"],

            "history":
            state["previous_history"]

        }

    )

    alternatives = result.model_dump()["alternatives"]

    from validators.task_validator import validate_task_duration, validate_and_adjust_task_schedule
    alternatives = validate_task_duration(
        tasks=alternatives,
        max_minutes=state["baseline"].get("daily_commitment_minutes", 50)
    )
    alternatives = validate_and_adjust_task_schedule(
        tasks=alternatives,
        preferred_time_ranges=state["baseline"].get("preferred_time_ranges", [])
    )

    import asyncio
    from utils.resource_helper import get_allowed_resource_types, fetch_and_validate_resources

    import httpx
    async def add_real_resources(t, client=None):
        baseline = state["baseline"]
        learning_preferences = baseline.get("learning_preferences", [])
        allowed = get_allowed_resource_types(learning_preferences)
        # Similar rules as task chunks: skip resources for physical tasks and
        # only include audio/video when the replacement explicitly requests it.
        text = " ".join([
            str(t.get("title", "")),
            str(t.get("description", "")),
            str(t.get("rationale", "")),
        ]).lower()

        physical_keywords = [
            "run", "walk", "jog", "lift", "squat", "press", "push",
            "pull", "stretch", "yoga", "exercise", "movement",
        ]
        requires_audio = any(w in text for w in ("listen", "hear", "podcast", "audio"))
        requires_video = any(w in text for w in ("watch", "watching", "video", "youtube"))
        wants_reading = any(w in text for w in ("read", "book", "article", "chapter"))

        if not (requires_audio or requires_video or wants_reading):
            if any(k in text for k in physical_keywords):
                t["resources"] = []
                return t

        # Intersect the task requirements with the user's allowed resource types
        filtered_allowed = []
        if requires_video and "video" in allowed:
            filtered_allowed.append("video")
        if requires_audio and "audio" in allowed:
            filtered_allowed.append("audio")
        if wants_reading:
            if "book" in allowed:
                filtered_allowed.append("book")
            if "article" in allowed:
                filtered_allowed.append("article")
        filtered_allowed = list(dict.fromkeys(filtered_allowed))

        from utils.resource_helper import ensure_fallback_resources, update_task_with_real_resources

        if not filtered_allowed:
            t["resources"] = []
            t = ensure_fallback_resources(t, allowed)
            t = update_task_with_real_resources(t)
            return t

        max_seconds = None
        try:
            max_seconds = int(t.get("duration_minutes", 0)) * 60
            if max_seconds <= 0:
                max_seconds = None
        except Exception:
            max_seconds = None

        t["resources"] = await fetch_and_validate_resources(t["title"], filtered_allowed, max_duration_seconds=max_seconds, client=client)
        t = ensure_fallback_resources(t, allowed)
        t = update_task_with_real_resources(t)
        return t

    async with httpx.AsyncClient() as client:
        alternatives = list(await asyncio.gather(*(add_real_resources(t, client) for t in alternatives)))

    state["alternatives"] = alternatives

    await state["db"].replacement_cache.delete_many(
        {
            "journey_id": state["journey_id"],
            "task_id": state["task_id"]
        }
    )

    await state["db"].replacement_cache.insert_one(

        {

            "journey_id": state["journey_id"],

            "task_id": state["task_id"],

            "alternatives": state["alternatives"],

            "expireAt": datetime.utcnow()
            + timedelta(minutes=30)

        }

    )

    return state