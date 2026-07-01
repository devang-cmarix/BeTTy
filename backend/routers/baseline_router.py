from fastapi import APIRouter
from fastapi import Depends

from database.mongodb import get_db
from models.baseline_model import BaselineModel

from services.baseline_service import (
    save_baseline
)

router = APIRouter(
    prefix="/baseline",
    tags=["Baseline"]
)


@router.post("/{aspiration_id}")
async def create_baseline(
        aspiration_id: str,
        payload: BaselineModel,
        db=Depends(get_db)
):

    result = await save_baseline(
        db,
        aspiration_id,
        payload.model_dump()
    )

    return result
