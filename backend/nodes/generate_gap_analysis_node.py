from langchain_core.prompts import ChatPromptTemplate

from prompts.gap_analysis_prompt import (
    GAP_ANALYSIS_PROMPT
)

from schemas.gap_analysis_schema import (
    GapAnalysisSchema
)

async def generate_gap_analysis_node(
        state
):

    llm = state["llm"]

    structured_llm = llm.with_structured_output(
        GapAnalysisSchema
    )

    prompt = ChatPromptTemplate.from_template(
        GAP_ANALYSIS_PROMPT
    )

    chain = prompt | structured_llm

    result = await chain.ainvoke(
        {
            "profile":
            state["profile"]
        }
    )

    state["gap_analysis"] = result.model_dump()

    return state