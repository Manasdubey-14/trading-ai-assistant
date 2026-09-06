from typing import Optional

from pydantic import BaseModel


class TechnicalEvidence(BaseModel):
    direction: str
    strength: float

    ema_signal: str
    rsi_signal: str
    macd_signal: str


class TrendEvidence(BaseModel):
    direction: str
    strength: float


class VolumeEvidence(BaseModel):
    status: str
    strength: float


class PatternEvidence(BaseModel):
    pattern: Optional[str] = None
    direction: str
    strength: float


class MarketRegimeEvidence(BaseModel):
    direction: str
    strength: float


class NewsEvidence(BaseModel):
    sentiment: str
    strength: float
    summary: Optional[str] = None


class RiskEvidence(BaseModel):
    status: str
    risk_reward: Optional[float] = None
    risk_score: Optional[float] = None


class MarketEvidence(BaseModel):
    symbol: str

    technical: Optional[TechnicalEvidence] = None
    trend: Optional[TrendEvidence] = None
    volume: Optional[VolumeEvidence] = None
    pattern: Optional[PatternEvidence] = None
    market_regime: Optional[MarketRegimeEvidence] = None
    news: Optional[NewsEvidence] = None
    risk: Optional[RiskEvidence] = None