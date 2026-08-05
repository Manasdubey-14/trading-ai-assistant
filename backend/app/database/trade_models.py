from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime

from datetime import datetime

from app.database.database import Base


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String, nullable=False)

    trade_type = Column(String, nullable=False)      # BUY / SELL

    quantity = Column(Integer, nullable=False)

    entry_price = Column(Float, nullable=False)

    exit_price = Column(Float, nullable=True)

    stop_loss = Column(Float, nullable=True)

    target = Column(Float, nullable=True)
    strategy = Column(
        String,
        nullable=True,
    )

    timeframe = Column(
        String,
        nullable=True,
    )

    confidence = Column(
        Float,
        nullable=True,
    )

    notes = Column(
        String,
        nullable=True,
    )

    pnl = Column(Float, default=0)

    status = Column(String, default="OPEN")

    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(
        DateTime,
        nullable=True,
    )