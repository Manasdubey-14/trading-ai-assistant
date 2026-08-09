from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class MarketSignal(Base):
    __tablename__ = "market_signals"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String, nullable=False)

    signal = Column(String, nullable=False)

    confidence = Column(Float, nullable=False)

    trend = Column(String, nullable=False)

    entry_price = Column(Float, nullable=True)

    stop_loss = Column(Float, nullable=True)

    target_price = Column(Float, nullable=True)

    strategy = Column(String, nullable=True)

    timeframe = Column(String, nullable=True)

    reason = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )