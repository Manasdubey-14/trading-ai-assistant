from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaperTradeCreate(BaseModel):
    symbol: str
    trade_type: str
    quantity: int
    entry_price: float
    stop_loss: float
    target: float


class PaperTradeResponse(BaseModel):
    id: int
    symbol: str
    trade_type: str
    quantity: int
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

    class Config:
        from_attributes = True