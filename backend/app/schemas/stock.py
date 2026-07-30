from pydantic import BaseModel


class EMAResponse(BaseModel):
    symbol: str
    indicator: str
    current_price: float
    ema: float
    signal: str


class RSIResponse(BaseModel):
    symbol: str
    indicator: str
    current_price: float
    rsi: float
    signal: str