from langchain_core.prompts import (
    ChatPromptTemplate
)


SUMMARY_PROMPT = """
You are an AI assistant.

Summarize the conversation.

Keep only important facts.

Include

Goals

Progress

Tasks

Important coaching advice

User preferences

Conversation

{conversation}
"""


async def summarize_memory_node(state):
    journey_id = state.get("journey_id")
    if not journey_id:
        return state

    history = state["history"]

    if len(history) < 20:

        return state

    prompt = ChatPromptTemplate.from_template(

        SUMMARY_PROMPT

    )

    chain = (

        prompt

        |

        state["llm"]

    )

    conversation = "\n".join(

        [

            f"{m['role']} : {m['content']}"

            for m in history

        ]

    )

    summary = await chain.ainvoke(

        {

            "conversation": conversation

        }

    )

    from tools.memory_tools import (

        update_summary

    )

    await update_summary(

        db=state["db"],

        journey_id=journey_id,

        summary=summary.content

    )

    state["conversation_summary"] = summary.content

    return state