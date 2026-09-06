from sqlalchemy.orm import Session

from app.database.signal_model import MarketSignal


class SignalRepository:

    @staticmethod
    def save(
        db: Session,
        signal: MarketSignal,
    ):
        existing_signal = (
            db.query(MarketSignal)
            .filter(
                MarketSignal.symbol == signal.symbol,
                MarketSignal.timeframe == signal.timeframe,
                MarketSignal.strategy == signal.strategy,
            )
            .order_by(MarketSignal.created_at.desc())
            .first()
        )

        if existing_signal:
            existing_signal.signal = signal.signal
            existing_signal.confidence = signal.confidence
            existing_signal.trend = signal.trend
            existing_signal.entry_price = signal.entry_price
            existing_signal.stop_loss = signal.stop_loss
            existing_signal.target_price = signal.target_price
            existing_signal.reason = signal.reason

            db.commit()
            db.refresh(existing_signal)

            return existing_signal

        db.add(signal)
        db.commit()
        db.refresh(signal)

        return signal

    @staticmethod
    def get_latest(
        db: Session,
        limit: int = 20,
    ):
        signals = (
            db.query(MarketSignal)
            .order_by(MarketSignal.created_at.desc())
            .all()
        )

        latest_by_symbol = {}

        for signal in signals:
            if signal.symbol not in latest_by_symbol:
                latest_by_symbol[signal.symbol] = signal

        return list(latest_by_symbol.values())[:limit]

    @staticmethod
    def count(
        db: Session,
    ):

        return db.query(MarketSignal).count()