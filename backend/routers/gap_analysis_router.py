from fastapi import APIRouter
from fastapi import Depends

from database.mongodb import get_db
from services.gap_analysis_service import (
    create_gap_analysis
)

router = APIRouter()

@router.post(
    "/gap-analysis/{journey_id}"
)
async def generate_gap_analysis(
        journey_id: str,
        db=Depends(get_db)
):

    result = await create_gap_analysis(
        db,
        journey_id
    )

    return result
