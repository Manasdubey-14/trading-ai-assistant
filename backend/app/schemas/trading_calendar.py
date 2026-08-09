from datetime import date

from pydantic import BaseModel


class TradingDayResponse(BaseModel):
    date: date
    is_trading_day: bool
    day_name: str
    reason: str