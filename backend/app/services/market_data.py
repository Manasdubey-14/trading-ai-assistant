import yfinance as yf
import pandas as pd

from app.analysis.indicators import (
    calculate_ema,
    calculate_rsi,
)


class MarketDataService:
    @staticmethod
    def get_stock_data(symbol: str):
        """
        Get current market data for a stock.
        """
        stock = yf.Ticker(symbol)
        info = stock.info

        return {
            "symbol": symbol,
            "company": info.get("longName"),
            "current_price": info.get("currentPrice"),
            "previous_close": info.get("previousClose"),
            "open": info.get("open"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "volume": info.get("volume"),
        }

    @staticmethod
    def get_history(
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ):
        """
        Get historical OHLCV data.
        """
        stock = yf.Ticker(symbol)

        history = stock.history(
            period=period,
            interval=interval,
        )

        if history.empty:
            return {
                "error": "No historical data found."
            }

        history.reset_index(inplace=True)

        history["Date"] = history["Date"].dt.strftime("%Y-%m-%d")

        history = history.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )

        history = history[
            [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ]

        history = history.round(
            {
                "open": 2,
                "high": 2,
                "low": 2,
                "close": 2,
            }
        )

        return history.to_dict(orient="records")

    @staticmethod
    def get_ema(
        symbol: str,
        period: int = 20,
        interval: str = "1d",
    ):
        """
        Calculate the latest EMA value.
        """
        stock = yf.Ticker(symbol)

        history = stock.history(
            period="6mo",
            interval=interval,
        )

        if history.empty:
            return {
                "error": "No historical data found."
            }

        history["EMA"] = calculate_ema(
            history,
            period,
        )

        latest = history.iloc[-1]

        signal = (
            "Bullish"
            if latest["Close"] > latest["EMA"]
            else "Bearish"
        )

        return {
            "symbol": symbol,
            "indicator": f"EMA {period}",
            "current_price": round(float(latest["Close"]), 2),
            "ema": round(float(latest["EMA"]), 2),
            "signal": signal,
        }