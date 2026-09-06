import unittest
from unittest.mock import patch

import pandas as pd

from app.services.market_data import MarketDataService
from app.services.market_regime_service import MarketRegimeService


def make_history(final_close: float) -> pd.DataFrame:
    return pd.DataFrame({
        "Close": [100.0] * 29 + [final_close],
    })


class MarketRegimeServiceTests(unittest.TestCase):

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_bullish_evidence_above_ema(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(110.0)

        evidence = (
            MarketRegimeService
            .get_market_regime_evidence()
        )

        self.assertEqual(evidence.direction, "Bullish")
        self.assertEqual(evidence.strength, 1.0)
        get_historical_data.assert_called_once_with(
            "^NSEI",
            period="6mo",
            interval="1d",
        )

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_bearish_evidence_below_ema(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(90.0)

        evidence = (
            MarketRegimeService
            .get_market_regime_evidence()
        )

        self.assertEqual(evidence.direction, "Bearish")
        self.assertEqual(evidence.strength, 1.0)

    @patch.object(MarketDataService, "get_historical_data")
    def test_returns_neutral_evidence_at_ema(
        self,
        get_historical_data,
    ):
        get_historical_data.return_value = make_history(100.0)

        evidence = (
            MarketRegimeService
            .get_market_regime_evidence()
        )

        self.assertEqual(evidence.direction, "Neutral")
        self.assertEqual(evidence.strength, 0.0)


if __name__ == "__main__":
    unittest.main()
