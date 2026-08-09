from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PositionResponse(BaseModel):
    id: int

    symbol: str
    side: str
    quantity: int

    entry_price: float
    current_price: float

    stop_loss: Optional[float] = None
    target: Optional[float] = None

    unrealized_pnl: float
    realized_pnl: float

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None