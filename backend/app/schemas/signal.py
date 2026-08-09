
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SignalResponse(BaseModel):
    symbol: str
    signal: str
    confidence: float
    trend: str

    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    risk_reward: Optional[float] = None

    reasons: list[str]

    created_at: Optional[datetime] = None


