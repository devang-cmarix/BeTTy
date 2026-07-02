from langchain_core.prompts import ChatPromptTemplate

from prompts.intent_prompt import (
    INTENT_PROMPT
)

from schemas.intent_schema import (
    IntentSchema
)


async def intent_node(state):

    llm = state["llm"]

    structured_llm = llm.with_structured_output(
        IntentSchema
    )

    prompt = ChatPromptTemplate.from_template(
        INTENT_PROMPT
    )

    chain = prompt | structured_llm

    result = await chain.ainvoke(
        {
            "message": state["user_message"]
        }
    )

    state["intent"] = result.model_dump()

    state["day"] = result.day

    state["keyword"] = result.keyword

    state["task_id"] = result.task_id
    
    return state