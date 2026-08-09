from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_signals: int

    buy_signals: int

    sell_signals: int

    wait_signals: int

    average_confidence: float

    top_signal: str | None = None