PLANNING_RULES = {

    ("ASPIRATION", "SHOW"): [

        {
            "domain": "ASPIRATION",
            "action": "SHOW"
        }

    ],

    ("BASELINE", "SHOW"): [

        {
            "domain": "BASELINE",
            "action": "SHOW"
        }

    ],

    ("GAP_ANALYSIS", "SHOW"): [

        {
            "domain": "GAP_ANALYSIS",
            "action": "SHOW"
        }

    ],

    ("GAP_ANALYSIS", "EXPLAIN"): [

        {
            "domain": "GAP_ANALYSIS",
            "action": "SHOW"
        },

        {
            "domain": "ASPIRATION",
            "action": "SHOW"
        }

    ],

    ("PLAN", "SHOW"): [

        {
            "domain": "PLAN",
            "action": "SHOW"
        }

    ],

    ("PLAN", "PROGRESS"): [

        {
            "domain": "PLAN",
            "action": "PROGRESS"
        }

    ],

    ("TASK", "TODAY"): [

        {
            "domain": "TASK",
            "action": "TODAY"
        }

    ],

    ("TASK", "SHOW"): [

        {
            "domain": "TASK",
            "action": "SHOW"
        }

    ],

    ("TASK", "EXPLAIN"): [

        {
            "domain": "TASK",
            "action": "TODAY"
        },

        {
            "domain": "GAP_ANALYSIS",
            "action": "SHOW"
        },

        {
            "domain": "ASPIRATION",
            "action": "SHOW"
        }

    ],

    ("TASK", "COMPLETE"): [

        {
            "domain": "TASK",
            "action": "TODAY"
        }

    ],

    ("TASK", "SKIP"): [

        {
            "domain": "TASK",
            "action": "TODAY"
        }

    ],

    ("TASK", "REPLACE"): [

        {
            "domain": "TASK",
            "action": "TODAY"
        }

    ],

    ("RESOURCE", "SEARCH"): [

        {
            "domain": "RESOURCE",
            "action": "SEARCH"
        }

    ],

    ("HISTORY", "SHOW"): [

        {
            "domain": "HISTORY",
            "action": "SHOW"
        }

    ],

    ("GENERAL", "CHAT"): []

}


async def planning_node(state):

    intent = state["intent"]

    key = (

        intent["domain"],

        intent["action"]

    )

    state["tool_plan"] = PLANNING_RULES.get(
        key,
        []
    )

    return state