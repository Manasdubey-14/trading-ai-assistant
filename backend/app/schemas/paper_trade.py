from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaperTradeCreate(BaseModel):
    symbol: str
    trade_type: str
    quantity: int

    # Backend fetches this automatically when omitted
    entry_price: float | None = None

    stop_loss: float
    target: float

    strategy: Optional[str] = None
    timeframe: Optional[str] = None
    confidence: Optional[float] = None
    notes: Optional[str] = None


class PaperTradeResponse(BaseModel):
    id: int
    symbol: str
    trade_type: str
    quantity: int

    # A created paper trade always has an entry price
    entry_price: float

    exit_price: Optional[float]
    stop_loss: Optional[float]
    target: Optional[float]

    strategy: Optional[str]
    timeframe: Optional[str]
    confidence: Optional[float]
    notes: Optional[str]

    pnl: float
    status: str

    created_at: datetime
    closed_at: Optional[datetime]
    exit_reason: Optional[str]

    class Config:
        from_attributes = True