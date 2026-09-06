import unittest
from unittest.mock import patch

import pandas as pd

from app.services.market_data import MarketDataService
from app.services.pattern_evidence_service import (
    PatternEvidenceService,
)


def make_history(
    previous_candle: dict[str, float],
    current_candle: dict[str, float],
) -> pd.DataFrame:
    return pd.DataFrame([
        previous_candle,
        current_candle,
    ])


class PatternEvidenceServiceTests(unittest.TestCase):

    @patch.object(MarketDataService, "get_historical_data")
    def test_detects_bullish_engulfing_pattern(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            {
                "Open": 110.0,
                "High": 112.0,
                "Low": 98.0,
                "Close": 100.0,
            },
            {
                "Open": 99.0,
                "High": 123.0,
                "Low": 97.0,
                "Close": 121.0,
            },
        )

        evidence = PatternEvidenceService.get_pattern_evidence(
            "RELIANCE.NS"
        )

        self.assertEqual(evidence.pattern, "Bullish Engulfing")
        self.assertEqual(evidence.direction, "Bullish")
        self.assertGreater(evidence.strength, 0.0)
        self.assertLessEqual(evidence.strength, 1.0)
        get_historical_data.assert_called_once_with(
            "RELIANCE.NS",
            period="6mo",
            interval="1d",
        )

    @patch.object(MarketDataService, "get_historical_data")
    def test_detects_bearish_engulfing_pattern(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            {
                "Open": 100.0,
                "High": 112.0,
                "Low": 98.0,
                "Close": 110.0,
            },
            {
                "Open": 111.0,
                "High": 113.0,
                "Low": 87.0,
                "Close": 89.0,
            },
        )

        evidence = PatternEvidenceService.get_pattern_evidence(
            "RELIANCE.NS"
        )

        self.assertEqual(evidence.pattern, "Bearish Engulfing")
        self.assertEqual(evidence.direction, "Bearish")
        self.assertGreater(evidence.strength, 0.0)
        self.assertLessEqual(evidence.strength, 1.0)

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_neutral_evidence_when_no_pattern_matches(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(
            {
                "Open": 100.0,
                "High": 107.0,
                "Low": 99.0,
                "Close": 105.0,
            },
            {
                "Open": 106.0,
                "High": 109.0,
                "Low": 104.0,
                "Close": 107.0,
            },
        )

        evidence = PatternEvidenceService.get_pattern_evidence(
            "RELIANCE.NS"
        )

        self.assertIsNone(evidence.pattern)
        self.assertEqual(evidence.direction, "Neutral")
        self.assertEqual(evidence.strength, 0.0)


if __name__ == "__main__":
    unittest.main()
