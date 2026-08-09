from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import MarketAnalytics


class AnalyticsService:

    @staticmethod
    def get_market_health(
        db: Session,
    ):

        total = AnalyticsRepository.total_signals(db)

        buy = AnalyticsRepository.buy_signals(db)

        sell = AnalyticsRepository.sell_signals(db)

        wait = AnalyticsRepository.wait_signals(db)

        average_confidence = (
            AnalyticsRepository.average_confidence(db)
        )

        strongest = (
            AnalyticsRepository.strongest_signal(db)
        )

        if total == 0:

            return MarketAnalytics(
                total_signals=0,
                bullish_percentage=0,
                bearish_percentage=0,
                neutral_percentage=0,
                average_confidence=0,
                market_health="Neutral",
                strongest_signal=None,
            )

        bullish_percentage = (
            buy / total
        ) * 100

        bearish_percentage = (
            sell / total
        ) * 100

        neutral_percentage = (
            wait / total
        ) * 100

        if bullish_percentage >= 50:

            market_health = "Bullish"

        elif bearish_percentage >= 50:

            market_health = "Bearish"

        else:

            market_health = "Neutral"

        return MarketAnalytics(

            total_signals=total,

            bullish_percentage=round(
                bullish_percentage,
                2,
            ),

            bearish_percentage=round(
                bearish_percentage,
                2,
            ),

            neutral_percentage=round(
                neutral_percentage,
                2,
            ),

            average_confidence=round(
                float(average_confidence),
                2,
            ),

            market_health=market_health,

            strongest_signal=(
                strongest.symbol
                if strongest
                else None
            ),
        )