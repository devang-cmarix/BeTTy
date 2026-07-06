from graphs.supervisor_graph import (
    supervisor_graph
)


def get_suggestions_for_intent(intent: dict) -> list:
    domain = intent.get("domain")
    action = intent.get("action")
    keyword = intent.get("keyword")
    day = intent.get("day")
    
    if keyword and (len(keyword) > 20 or keyword.strip().lower() in ["hello", "hi", "hey"]):
        keyword = None
        
    sugs = []
    
    if domain == "ASPIRATION" and action == "SHOW":
        if keyword:
            sugs = [
                f"gap analysis of {keyword}",
                f"progress of {keyword}",
                f"day 1 plan of {keyword}"
            ]
        else:
            sugs = ["Root Causes", "Gap Analysis", "Progress", "My Tasks"]
            
    elif domain == "GAP_ANALYSIS" and action == "SHOW":
        if keyword:
            sugs = [
                f"obstacles of {keyword}",
                f"progress of {keyword}",
                f"day 1 plan of {keyword}"
            ]
        else:
            sugs = ["Current State", "Future State", "Obstacles", "My Tasks"]
            
    elif domain == "BASELINE" and action == "SHOW":
        sugs = ["Core Values", "Motives", "Obstacles", "Gap Analysis"]
        
    elif domain == "PLAN" and (action in ["SHOW", "PROGRESS"]):
        if keyword:
            sugs = [
                f"day 1 plan of {keyword}",
                f"gap analysis of {keyword}",
                f"progress of {keyword}"
            ]
        else:
            sugs = ["My Tasks", "Week Summary", "Progress"]
            
    elif domain == "TASK" or domain == "RESOURCE":
        if day is not None:
            sugs = [
                f"day {day + 1} task",
                "why this task?",
                "My Tasks"
            ]
        else:
            sugs = ["complete it", "why this task?", "My Tasks"]
            
    else:
        sugs = ["My Aspiration", "Gap Analysis", "Progress", "My Tasks"]
        
    return sugs


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

        intent = result.get("intent", {})
        suggestions = get_suggestions_for_intent(intent)

        return {

            "reply": result["response"],

            "intent": result["intent"],

            "sources": result["tool_results"],

            "suggestions": suggestions

        }