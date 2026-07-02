from tools.memory_tools import (
    load_memory
)


async def load_memory_node(state):
    journey_id = state.get("journey_id")
    if not journey_id:
        # If no journey_id is provided, we do not attempt to load from database.
        # We keep the history passed in from the frontend.
        state["conversation_summary"] = ""
        return state

    memory = await load_memory(

        state["db"],

        journey_id

    )

    # Use database history if available, otherwise fallback to frontend history
    if memory.get("messages"):
        state["history"] = memory["messages"]

    state["conversation_summary"] = memory.get("summary", "")

    return state