from fastapi import APIRouter, Query
from pydantic import BaseModel
from services.force_service import (
    classify_force,
    get_all_forces,
    get_force,
    get_root_causes
)

router = APIRouter()


class ForceClassificationRequest(BaseModel):
    text: str


@router.get("/forces")
def forces():

    return get_all_forces()


@router.post("/forces/classify")
def force_classification(request: ForceClassificationRequest):

    if not request.text.strip():
        return {"error": "Please enter what you want to improve."}

    return classify_force(request.text)


@router.get("/forces/{slug}")
def force_details(slug: str):

    force = get_force(slug)

    if not force:
        return {"error": "Force not found"}

    return {
        "question": force["question"],
        "options": force["details"]
    }


@router.get("/forces/{slug}/detail")
def root_causes(slug: str, detail: str = Query(...)):

    result = get_root_causes(slug, detail)

    if not result:
        return {"error": "Not found"}

    return result
