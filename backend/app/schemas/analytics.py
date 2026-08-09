from pydantic import BaseModel


class MarketAnalytics(BaseModel):

    total_signals: int

    bullish_percentage: float

    bearish_percentage: float

    neutral_percentage: float

    average_confidence: float

    market_health: str

    strongest_signal: str | None = None