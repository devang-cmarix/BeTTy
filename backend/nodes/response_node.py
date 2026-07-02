from langchain_core.prompts import (
    ChatPromptTemplate
)

from prompts.response_prompt import (
    RESPONSE_PROMPT
)


async def response_node(state):

    prompt = ChatPromptTemplate.from_template(

        RESPONSE_PROMPT

    )

    chain = (

        prompt

        |

        state["llm"]

    )

    result = await chain.ainvoke(

        {

            "context": state["formatted_context"],

            "summary": state["conversation_summary"],
            
            "history": state["history"],

            "question": state["user_message"]

        }

    )

    state["response"] = result.content

    return state