from math import isfinite

from app.analysis.ema import calculate_ema
from app.schemas.evidence import MarketRegimeEvidence
from app.services.market_data import MarketDataService


class MarketRegimeService:
    """Derive broad-market evidence from the NIFTY 50 daily trend."""

    MARKET_INDEX_SYMBOL = "^NSEI"
    EMA_PERIOD = 20

    # A 5% distance from the 20-day EMA represents full technical evidence.
    # This is a normalized evidence scale, never a probability of profit.
    FULL_STRENGTH_DISTANCE_PERCENT = 5.0

    @classmethod
    def get_market_regime_evidence(
        cls,
    ) -> MarketRegimeEvidence:
        """
        Evaluate the NIFTY 50 against its 20-day EMA.

        Market data is intentionally obtained through MarketDataService so
        this layer shares the existing cache and does not fetch independently.
        """
        history = MarketDataService.get_historical_data(
            cls.MARKET_INDEX_SYMBOL,
            period="6mo",
            interval="1d",
        )

        if history.empty or "Close" not in history:
            raise ValueError(
                "No NIFTY 50 historical data available "
                "for market-regime evidence."
            )

        history = history.dropna(subset=["Close"]).copy()

        if len(history) < cls.EMA_PERIOD:
            raise ValueError(
                "Insufficient NIFTY 50 history for "
                f"a {cls.EMA_PERIOD}-day EMA."
            )

        history["EMA"] = calculate_ema(
            history,
            period=cls.EMA_PERIOD,
        )

        latest_close = float(history["Close"].iloc[-1])
        latest_ema = float(history["EMA"].iloc[-1])

        if (
            not isfinite(latest_close)
            or not isfinite(latest_ema)
            or latest_ema <= 0
        ):
            raise ValueError(
                "Invalid NIFTY 50 close or EMA value "
                "for market-regime evidence."
            )

        if latest_close > latest_ema:
            direction = "Bullish"
        elif latest_close < latest_ema:
            direction = "Bearish"
        else:
            direction = "Neutral"

        distance_percent = abs(
            (latest_close - latest_ema) / latest_ema
        ) * 100

        strength = min(
            distance_percent
            / cls.FULL_STRENGTH_DISTANCE_PERCENT,
            1.0,
        )

        return MarketRegimeEvidence(
            direction=direction,
            strength=round(strength, 2),
        )
