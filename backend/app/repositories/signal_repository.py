from sqlalchemy.orm import Session

from app.database.signal_model import MarketSignal


class SignalRepository:

    @staticmethod
    def save(
        db: Session,
        signal: MarketSignal,
    ):

        db.add(signal)
        db.commit()
        db.refresh(signal)

        return signal

    @staticmethod
    def get_latest(
        db: Session,
        limit: int = 20,
    ):

        return (
            db.query(MarketSignal)
            .order_by(MarketSignal.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def count(
        db: Session,
    ):

        return db.query(MarketSignal).count()