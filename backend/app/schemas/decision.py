from pydantic import BaseModel


class DecisionResponse(BaseModel):
    symbol: str

    signal: str

    confidence: float

    trend: str

    reasons: list[str]