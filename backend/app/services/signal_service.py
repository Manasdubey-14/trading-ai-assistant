from sqlalchemy.orm import Session

from app.database.signal_model import MarketSignal
from app.repositories.signal_repository import SignalRepository
from app.schemas.signal import SignalResponse



class SignalService:

    @staticmethod
    def save_signal(
        db: Session,
        signal: SignalResponse,
    ):

        market_signal = MarketSignal(
            symbol=signal.symbol,
            signal=signal.signal,
            confidence=signal.confidence,
            trend=signal.trend,
            entry_price=signal.entry,
            stop_loss=signal.stop_loss,
            target_price=signal.target,
            strategy="Default Strategy",
            timeframe="1D",
            reason=", ".join(signal.reasons),
        )

        return SignalRepository.save(
            db,
            market_signal,
        )

    
    @staticmethod
    def get_latest_signals(
        db: Session,
        limit: int = 20,
    ):

        signals = SignalRepository.get_latest(
            db,
            limit,
        )

        response = []

        for signal in signals:

            response.append(
                SignalResponse(
                    symbol=signal.symbol,
                    signal=signal.signal,
                    confidence=signal.confidence,
                    trend=signal.trend,
                    entry=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    target=signal.target_price,
                    risk_reward=None,
                    reasons=signal.reason.split(", "),
                    created_at=signal.created_at,
                )
            )

        return response