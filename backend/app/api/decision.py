from fastapi import APIRouter

from app.schemas.decision import DecisionResponse
from app.services.decision_service import DecisionService

router = APIRouter(
    prefix="/decision",
    tags=["Decision Engine"],
)


@router.get(
    "/{symbol}",
    response_model=DecisionResponse,
)
def analyze_stock(symbol: str):
    return DecisionService.analyze(symbol)