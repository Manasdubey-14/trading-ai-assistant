from pydantic import BaseModel


class Opportunity(BaseModel):
    rank: int

    symbol: str

    signal: str

    confidence: float

    score: float

    strength: str

    trend: str

    entry: float | None = None

    target: float | None = None

    stop_loss: float | None = None

    risk_reward: float | None = None