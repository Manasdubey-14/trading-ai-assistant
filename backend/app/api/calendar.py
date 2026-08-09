from datetime import date

from fastapi import APIRouter

from app.schemas.trading_calendar import TradingDayResponse
from app.services.trading_calendar_service import (
    TradingCalendarService,
)


router = APIRouter(
    prefix="/calendar",
    tags=["Trading Calendar"],
)


@router.get(
    "/{requested_date}",
    response_model=TradingDayResponse,
)
def get_trading_day(
    requested_date: date,
):

    return TradingCalendarService.get_day_info(
        requested_date
    )