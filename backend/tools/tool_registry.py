from tools.aspiration_tools import get_aspiration
from tools.baseline_tools import get_baseline
from tools.gap_tools import get_gap_analysis
from tools.plan_tools import (
    get_plan,
    get_plan_summary
)
from tools.task_tools import (
    get_today_task,
    get_task_by_day,
    search_tasks
)
from tools.history_tools import (
    get_replacement_history
)


TOOLS = {

    "ASPIRATION": {

        "SHOW": {

            "function": get_aspiration,

            "requires": [

                "journey_id"

            ]

        }

    },

    "BASELINE": {

        "SHOW": {

            "function": get_baseline,

            "requires": [

                "journey_id"

            ]

        }

    },

    "GAP_ANALYSIS": {

        "SHOW": {

            "function": get_gap_analysis,

            "requires": [

                "journey_id"

            ]

        },

        "EXPLAIN": {

            "function": get_gap_analysis,

            "requires": [

                "journey_id"

            ]

        }

    },

    "PLAN": {

        "SHOW": {

            "function": get_plan,

            "requires": [

                "journey_id"

            ]

        },

        "PROGRESS": {

            "function": get_plan_summary,

            "requires": [

                "journey_id"

            ]

        }

    },

    "TASK": {

        "TODAY": {

            "function": get_today_task,

            "requires": [

                "journey_id",

                "day"

            ]

        },

        "SHOW": {

            "function": get_task_by_day,

            "requires": [

                "journey_id",

                "day"

            ]

        },

        "SEARCH": {

            "function": search_tasks,

            "requires": [

                "journey_id",

                "keyword"

            ]

        }

    },

    "HISTORY": {

        "SHOW": {

            "function": get_replacement_history,

            "requires": [

                "journey_id"

            ]

        }

    }

}


def get_tool(
    domain: str,
    action: str
):

    domain_tools = TOOLS.get(domain)

    if domain_tools is None:

        raise ValueError(
            f"Unknown domain '{domain}'"
        )

    tool = domain_tools.get(action)

    if tool is None:

        raise ValueError(
            f"Unsupported action '{action}' for domain '{domain}'"
        )

    return tool