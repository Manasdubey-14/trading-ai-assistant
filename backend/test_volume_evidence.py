import unittest
from unittest.mock import patch

import pandas as pd

from app.services.market_data import MarketDataService
from app.services.volume_evidence_service import (
    VolumeEvidenceService,
)


def make_history(
    final_close: float,
    final_volume: float,
) -> pd.DataFrame:
    return pd.DataFrame({
        "Close": [100.0] * 20 + [final_close],
        "Volume": [100.0] * 20 + [final_volume],
    })


class VolumeEvidenceServiceTests(unittest.TestCase):

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_bullish_evidence_for_rising_price_and_high_volume(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            final_close=110.0,
            final_volume=200.0,
        )

        evidence = VolumeEvidenceService.get_volume_evidence(
            "RELIANCE.NS"
        )

        self.assertEqual(evidence.status, "Bullish")
        self.assertEqual(evidence.strength, 1.0)
        get_historical_data.assert_called_once_with(
            "RELIANCE.NS",
            period="6mo",
            interval="1d",
        )

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_bearish_evidence_for_falling_price_and_high_volume(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            final_close=90.0,
            final_volume=200.0,
        )

        evidence = VolumeEvidenceService.get_volume_evidence(
            "RELIANCE.NS"
        )

        self.assertEqual(evidence.status, "Bearish")
        self.assertEqual(evidence.strength, 1.0)

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_weak_evidence_for_below_normal_volume(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            final_close=110.0,
            final_volume=80.0,
        )

        evidence = VolumeEvidenceService.get_volume_evidence(
            "RELIANCE.NS"
        )

        self.assertEqual(evidence.status, "Weak")
        self.assertEqual(evidence.strength, 0.0)

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_neutral_evidence_without_price_direction(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            final_close=100.0,
            final_volume=200.0,
        )

        evidence = VolumeEvidenceService.get_volume_evidence(
            "RELIANCE.NS"
        )

        self.assertEqual(evidence.status, "Neutral")
        self.assertEqual(evidence.strength, 0.0)


if __name__ == "__main__":
    unittest.main()
