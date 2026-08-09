from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.database import Base


class Position(Base):

    __tablename__ = "positions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    symbol = Column(
        String,
        nullable=False,
        index=True,
    )

    side = Column(
        String,
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    entry_price = Column(
        Float,
        nullable=False,
    )

    current_price = Column(
        Float,
        nullable=False,
    )

    stop_loss = Column(
        Float,
        nullable=True,
    )

    target = Column(
        Float,
        nullable=True,
    )

    realized_pnl = Column(
        Float,
        default=0.0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )