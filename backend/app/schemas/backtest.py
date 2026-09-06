from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):

    symbol: str

    period: str = "1y"

    interval: str = "1d"

    quantity: int = Field(
        default=1,
        ge=1,
    )

    slippage_percent: float = Field(
        default=0.0,
        ge=0,
    )

    transaction_cost_percent: float = Field(
        default=0.0,
        ge=0,
    )