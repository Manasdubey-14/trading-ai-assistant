from math import isfinite

from app.schemas.evidence import PatternEvidence
from app.services.market_data import MarketDataService


class PatternEvidenceService:
    """Detect a small, deterministic set of daily candlestick patterns."""

    @classmethod
    def get_pattern_evidence(
        cls,
        symbol: str,
    ) -> PatternEvidence:
        """
        Detect a bullish or bearish engulfing pattern in the last two candles.

        MarketDataService supplies the existing cached OHLCV history. Pattern
        strength reflects the clarity of the candle structure, not probability.
        """
        history = MarketDataService.get_historical_data(
            symbol,
            period="6mo",
            interval="1d",
        )

        required_columns = {"Open", "High", "Low", "Close"}

        if history.empty or not required_columns.issubset(history):
            raise ValueError(
                "No complete OHLC data available "
                "for pattern evidence."
            )

        history = history.dropna(
            subset=["Open", "High", "Low", "Close"]
        ).copy()

        if len(history) < 2:
            raise ValueError(
                "At least two candles are required "
                "for pattern evidence."
            )

        previous = history.iloc[-2]
        current = history.iloc[-1]

        previous_open = float(previous["Open"])
        previous_high = float(previous["High"])
        previous_low = float(previous["Low"])
        previous_close = float(previous["Close"])

        current_open = float(current["Open"])
        current_high = float(current["High"])
        current_low = float(current["Low"])
        current_close = float(current["Close"])

        values = [
            previous_open,
            previous_high,
            previous_low,
            previous_close,
            current_open,
            current_high,
            current_low,
            current_close,
        ]

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "Invalid OHLC values for pattern evidence."
            )

        if (
            previous_high < previous_low
            or current_high < current_low
        ):
            raise ValueError(
                "Invalid candle range for pattern evidence."
            )

        previous_body = abs(previous_close - previous_open)
        current_body = abs(current_close - current_open)

        if previous_body == 0 or current_body == 0:
            return cls._neutral_evidence()

        is_bullish_engulfing = (
            previous_close < previous_open
            and current_close > current_open
            and current_open <= previous_close
            and current_close >= previous_open
        )

        is_bearish_engulfing = (
            previous_close > previous_open
            and current_close < current_open
            and current_open >= previous_close
            and current_close <= previous_open
        )

        if is_bullish_engulfing:
            return cls._engulfing_evidence(
                pattern="Bullish Engulfing",
                direction="Bullish",
                previous_body=previous_body,
                current_body=current_body,
                current_high=current_high,
                current_low=current_low,
            )

        if is_bearish_engulfing:
            return cls._engulfing_evidence(
                pattern="Bearish Engulfing",
                direction="Bearish",
                previous_body=previous_body,
                current_body=current_body,
                current_high=current_high,
                current_low=current_low,
            )

        return cls._neutral_evidence()

    @staticmethod
    def _engulfing_evidence(
        pattern: str,
        direction: str,
        previous_body: float,
        current_body: float,
        current_high: float,
        current_low: float,
    ) -> PatternEvidence:
        current_range = current_high - current_low
        body_fraction = (
            current_body / current_range
            if current_range > 0
            else 0.0
        )

        # A body twice as large as the preceding body is full engulfing
        # evidence. Averaging it with body-to-range clarity keeps the score
        # bounded and deterministic.
        engulfing_strength = min(
            current_body / (previous_body * 2),
            1.0,
        )
        strength = (engulfing_strength + body_fraction) / 2

        return PatternEvidence(
            pattern=pattern,
            direction=direction,
            strength=round(strength, 2),
        )

    @staticmethod
    def _neutral_evidence() -> PatternEvidence:
        return PatternEvidence(
            pattern=None,
            direction="Neutral",
            strength=0.0,
        )
