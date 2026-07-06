from tools.tool_registry import (
    get_tool
)


async def tool_router_node(state):

    results = {}
    db = state["db"]
    active_journey_id = state.get("journey_id")
    keyword = state.get("keyword")

    resolved_journey_id = active_journey_id
    if keyword:
        try:
            cursor = db.aspirations.find({"baseline": {"$exists": True}}, {"input.force": 1})
            async for doc in cursor:
                force = doc.get("input", {}).get("force", "")
                if force:
                    kw_words = [w for w in keyword.lower().replace("/", " ").replace("-", " ").split() if len(w) > 2]
                    force_words = [w for w in force.lower().replace("/", " ").replace("-", " ").split() if len(w) > 2]
                    matched = False
                    for kw in kw_words:
                        for fw in force_words:
                            if kw in fw or fw in kw:
                                matched = True
                                break
                        if matched:
                            break
                    if matched:
                        resolved_journey_id = str(doc["_id"])
                        break
        except Exception:
            pass

    if not resolved_journey_id:
        try:
            doc = await db.aspirations.find_one({"baseline": {"$exists": True}}, {"_id": 1})
            if doc:
                resolved_journey_id = str(doc["_id"])
        except Exception:
            pass

    for step in state["tool_plan"]:

        domain = step["domain"]
        action = step["action"]

        try:
            tool_info = get_tool(

                domain,

                action

            )

            tool = tool_info["function"]

            required = tool_info["requires"]

            kwargs = {}

            for arg in required:

                if arg not in state:

                    continue

                if arg == "journey_id":
                    kwargs[arg] = resolved_journey_id
                else:
                    kwargs[arg] = state[arg]

            output = await tool(

                state["db"],

                **kwargs

            )
        except Exception as e:
            if action == "SEARCH" or domain == "HISTORY":
                output = []
            else:
                output = {"exists": False, "error": str(e)}

        results[

            f"{domain}_{action}"

        ] = output

    state["tool_results"] = results

    state["retrieved_context"] = results

    return state