from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.trading_analytics_service import (
    TradingAnalyticsService,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Trading Analytics"],
)


@router.get("/summary")
def get_trading_summary(
    db: Session = Depends(get_db),
):
    return TradingAnalyticsService.get_summary(
        db
    )