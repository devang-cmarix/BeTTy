async def load_plan_context_node(state):

    profile = state["profile"]

    state["aspiration"] = profile.get(
        "aspiration",
        {}
    )

    state["baseline"] = profile.get(
        "baseline",
        {}
    )

    state["gap_analysis"] = profile.get(
        "gap_analysis",
        {}
    )

    return state