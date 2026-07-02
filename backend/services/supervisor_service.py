from graphs.supervisor_graph import (
    supervisor_graph
)


class SupervisorService:

    def __init__(
        self,
        db,
        llm
    ):
        self.db = db
        self.llm = llm

    async def chat(

        self,

        journey_id: str,

        message: str,

        history: list

    ):

        state = {

            "db": self.db,

            "llm": self.llm,

            "journey_id": journey_id,

            "user_message": message,

            "history": history,

            "intent": {},

            "tool_plan": [],

            "tool_results": {},

            "retrieved_context": {},

            "response": "",

            "response_sources": [],

            "day": None,

            "keyword": None,

            "task_id": None,

            "formatted_context": "",

            "conversation_summary": ""

        }

        result = await supervisor_graph.ainvoke(state) # type: ignore

        return {

            "reply": result["response"],

            "intent": result["intent"],

            "sources": result["tool_results"]

        }