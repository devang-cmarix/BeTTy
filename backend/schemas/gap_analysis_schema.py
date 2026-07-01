from pydantic import BaseModel
from typing import List


class GapAnalysisSchema(BaseModel):

    where_i_am: str

    where_i_want_to_be: str

    my_obstacles: List[str]

    my_success_criteria: List[str]