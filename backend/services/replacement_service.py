from graphs.generate_alternatives_graph import (
    generate_alternatives_graph
)

from graphs.apply_replacement_graph import (
    apply_replacement_graph
)


class ReplacementService:

    def __init__(
        self,
        db,
        llm
    ):
        self.db = db
        self.llm = llm

    async def generate_alternatives(
        self,
        journey_id: str,
        task_id: str
    ):

        state = {

            "db": self.db,

            "llm": self.llm,

            "journey_id": journey_id,

            "task_id": task_id,

            "alternative_id": "",

            "profile": {},

            "aspiration": {},

            "baseline": {},

            "gap_analysis": {},

            "complete_plan": {},

            "current_task": {},

            "previous_history": [],

            "alternatives": [],

            "updated_task": {}

        }

        result = await generate_alternatives_graph.ainvoke(
            state
        )

        return result["alternatives"]

    async def apply_replacement(
        self,
        journey_id: str,
        task_id: str,
        alternative_id: str
    ):

        state = {

            "db": self.db,

            "llm": self.llm,

            "journey_id": journey_id,

            "task_id": task_id,

            "alternative_id": alternative_id,

            "profile": {},

            "aspiration": {},

            "baseline": {},

            "gap_analysis": {},

            "complete_plan": {},

            "current_task": {},

            "previous_history": [],

            "alternatives": [],

            "updated_task": {}

        }

        result = await apply_replacement_graph.ainvoke(
            state
        )

        return result["updated_task"]