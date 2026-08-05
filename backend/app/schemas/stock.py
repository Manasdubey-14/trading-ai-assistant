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


class MACDResponse(BaseModel):
    symbol: str
    current_price: float
    macd: float
    signal_line: float
    histogram: float
    signal: str

class AnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    ema: EMAResponse
    rsi: RSIResponse
    macd: MACDResponse