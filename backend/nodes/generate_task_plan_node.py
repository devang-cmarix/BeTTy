from langchain_core.prompts import (
    ChatPromptTemplate
)

from prompts.task_plan_prompt import (
    TASK_PLAN_PROMPT
)

from schemas.task_plan_schema import (
    TaskPlan
)
async def generate_task_plan_node(
        state
):

    profile = state["profile"]

    baseline = profile["baseline"]

    structured_llm = (
        state["llm"]
        .with_structured_output(
            TaskPlan
        )
    )

    chain = (
        ChatPromptTemplate
        .from_template(
            TASK_PLAN_PROMPT
        )
        | structured_llm
    )

    result = await chain.ainvoke(
        {
            "force":
                profile["force"],

            "issue":
                profile["issue"],

            "root_causes":
                profile["root_causes"],

            "aspiration":
                profile["aspiration"],

            "baseline":
                baseline,

            "gap_analysis":
                state["gap_analysis"],

            "user_notes":
                baseline.get(
                    "notes",
                    ""
                ),

            "plan_days":
                profile[
                    "aspiration"
                ][
                    "plan_duration"
                ]
        }
    )

    state["final_plan"] = (
        result.model_dump()
    )

    return state