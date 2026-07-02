from tools.tool_registry import (
    get_tool
)


async def tool_router_node(state):

    results = {}

    for step in state["tool_plan"]:

        tool_info = get_tool(

            step["domain"],

            step["action"]

        )

        tool = tool_info["function"]

        required = tool_info["requires"]

        kwargs = {}

        for arg in required:

            if arg not in state:

                continue

            kwargs[arg] = state[arg]

        output = await tool(

            state["db"],

            **kwargs

        )

        results[

            f"{step['domain']}_{step['action']}"

        ] = output

    state["tool_results"] = results

    state["retrieved_context"] = results

    return state