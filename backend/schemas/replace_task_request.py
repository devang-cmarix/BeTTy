from pydantic import BaseModel


class ReplaceTaskRequest(BaseModel):

    alternative_id: str