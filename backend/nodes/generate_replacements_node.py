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

    state["alternatives"] = (
        result.model_dump()["alternatives"]
    )

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