from tools.memory_tools import (
    save_user_message,
    save_assistant_message
)


async def save_memory_node(state):
    journey_id = state.get("journey_id")
    if not journey_id:
        return state

    await save_user_message(

        db=state["db"],

        journey_id=journey_id,

        message=state["user_message"]

    )

    tools = list(

        state["tool_results"].keys()

    )

    await save_assistant_message(

        db=state["db"],

        journey_id=journey_id,

        message=state["response"],

        intent=state["intent"],

        tools=tools

    )

    return state