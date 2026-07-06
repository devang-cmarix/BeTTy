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

    history = state.get("history", [])
    formatted_history = ""
    if history:
        lines = []
        for m in history:
            role = m.get('role', m.get('type', 'user'))
            content = m.get('content', '')
            lines.append(f"{role}: {content}")
            intent = m.get('intent')
            if intent:
                lines.append(f"  [Intent Metadata: domain={intent.get('domain')}, action={intent.get('action')}, day={intent.get('day')}]")
        formatted_history = "\n".join(lines)

    result = await chain.ainvoke(
        {
            "message": state["user_message"],
            "history": formatted_history
        }
    )

    state["intent"] = result.model_dump()

    state["day"] = result.day

    state["keyword"] = result.keyword or state["user_message"]

    state["task_id"] = result.task_id
    
    return state