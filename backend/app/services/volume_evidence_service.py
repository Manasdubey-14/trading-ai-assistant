from math import isfinite

from app.schemas.evidence import VolumeEvidence
from app.services.market_data import MarketDataService


class VolumeEvidenceService:
    """Derive price-confirming volume evidence for an instrument."""

    VOLUME_LOOKBACK = 20

    # A volume level at least twice the trailing average is full evidence.
    # This is a normalized evidence scale, never a probability of profit.
    FULL_STRENGTH_VOLUME_RATIO = 2.0

    @classmethod
    def get_volume_evidence(
        cls,
        symbol: str,
    ) -> VolumeEvidence:
        """
        Compare the latest daily volume with the previous 20 sessions.

        Above-normal volume confirms the latest daily price direction. The
        shared MarketDataService provides the history and existing cache.
        """
        history = MarketDataService.get_historical_data(
            symbol,
            period="6mo",
            interval="1d",
        )

        required_columns = {"Close", "Volume"}

        if history.empty or not required_columns.issubset(history):
            raise ValueError(
                "No complete OHLCV data available "
                "for volume evidence."
            )

        history = history.dropna(
            subset=["Close", "Volume"]
        ).copy()

        if len(history) <= cls.VOLUME_LOOKBACK:
            raise ValueError(
                "Insufficient OHLCV history for "
                f"a {cls.VOLUME_LOOKBACK}-session volume baseline."
            )

        latest_close = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2])
        latest_volume = float(history["Volume"].iloc[-1])
        normal_volume = float(
            history["Volume"]
            .iloc[-(cls.VOLUME_LOOKBACK + 1):-1]
            .mean()
        )

        values = [
            latest_close,
            previous_close,
            latest_volume,
            normal_volume,
        ]

        if not all(isfinite(value) for value in values):
            raise ValueError(
                "Invalid close or volume values "
                "for volume evidence."
            )

        if normal_volume <= 0:
            raise ValueError(
                "Normal volume must be greater than zero "
                "for volume evidence."
            )

        volume_ratio = latest_volume / normal_volume

        if volume_ratio <= 1.0:
            return VolumeEvidence(
                status="Weak",
                strength=0.0,
            )

        if latest_close > previous_close:
            status = "Bullish"
        elif latest_close < previous_close:
            status = "Bearish"
        else:
            return VolumeEvidence(
                status="Neutral",
                strength=0.0,
            )

        strength = min(
            (volume_ratio - 1)
            / (cls.FULL_STRENGTH_VOLUME_RATIO - 1),
            1.0,
        )

        return VolumeEvidence(
            status=status,
            strength=round(strength, 2),
        )
