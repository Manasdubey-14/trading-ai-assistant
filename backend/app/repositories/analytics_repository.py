from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.signal_model import MarketSignal


class AnalyticsRepository:

    @staticmethod
    def total_signals(db: Session):
        return db.query(MarketSignal).count()

    @staticmethod
    def buy_signals(db: Session):
        return (
            db.query(MarketSignal)
            .filter(MarketSignal.signal == "BUY")
            .count()
        )

    @staticmethod
    def sell_signals(db: Session):
        return (
            db.query(MarketSignal)
            .filter(MarketSignal.signal == "SELL")
            .count()
        )

    @staticmethod
    def wait_signals(db: Session):
        return (
            db.query(MarketSignal)
            .filter(MarketSignal.signal == "WAIT")
            .count()
        )

    @staticmethod
    def average_confidence(db: Session):
        return (
            db.query(func.avg(MarketSignal.confidence))
            .scalar()
            or 0
        )

    @staticmethod
    def strongest_signal(db: Session):
        return (
            db.query(MarketSignal)
            .order_by(MarketSignal.confidence.desc())
            .first()
        )