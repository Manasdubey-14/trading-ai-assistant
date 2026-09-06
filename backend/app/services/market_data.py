import time
import threading

import yfinance as yf

from app.analysis.indicators import (
    calculate_ema,
    calculate_rsi,
    calculate_macd,
)


class MarketDataService:

    # Development cache.
    # This MUST be replaced with market-session-aware caching
    # before live trading / F&O integration.
    _history_cache = {}
    _cache_lock = threading.Lock()
    CACHE_TTL = 300  # 5 minutes

    @classmethod
    def _get_cached_history(
        cls,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ):
        cache_key = (symbol, period, interval)
        now = time.time()

        with cls._cache_lock:
            cached = cls._history_cache.get(cache_key)

            if cached is not None:
                timestamp, history = cached

                if now - timestamp < cls.CACHE_TTL:
                    return history.copy()

        stock = yf.Ticker(symbol)

        history = stock.history(
            period=period,
            interval=interval,
            auto_adjust=False,
        )

        with cls._cache_lock:
            cls._history_cache[cache_key] = (
                now,
                history.copy(),
            )

        return history.copy()

    @classmethod
    def preload_history(
        cls,
        symbols: list[str],
        period: str = "6mo",
        interval: str = "1d",
    ):
        """
        Download historical data for multiple symbols in one yfinance request
        and populate the existing development cache.
        """
        if not symbols:
            return

        unique_symbols = list(dict.fromkeys(symbols))
        cache_key_suffix = (period, interval)
        now = time.time()

        # Only download symbols that are not already cached.
        symbols_to_download = []

        with cls._cache_lock:
            for symbol in unique_symbols:
                cache_key = (symbol, *cache_key_suffix)
                cached = cls._history_cache.get(cache_key)

                if cached is not None:
                    timestamp, _ = cached

                    if now - timestamp < cls.CACHE_TTL:
                        continue

                symbols_to_download.append(symbol)

        if not symbols_to_download:
            return

        data = yf.download(
            symbols_to_download,
            period=period,
            interval=interval,
            auto_adjust=False,
            group_by="ticker",
            threads=True,
            progress=False,
        )

        if data.empty:
            return

        with cls._cache_lock:
            for symbol in symbols_to_download:
                try:
                    # Multiple-symbol downloads return:
                    # (Ticker, Price)
                    if len(symbols_to_download) == 1:
                        history = data.copy()
                    else:
                        if symbol not in data.columns.get_level_values(0):
                            continue

                        history = data[symbol].copy()

                    if history.empty:
                        continue

                    cls._history_cache[
                        (symbol, period, interval)
                    ] = (
                        now,
                        history.copy(),
                    )

                except Exception as exc:
                    print(
                        f"[MarketData] Failed to cache {symbol}: {exc}"
                    )
                    
    @classmethod
    def clear_cache(cls):
        """Clear development market-data cache."""
        with cls._cache_lock:
            cls._history_cache.clear()

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

    @classmethod
    def get_history(
        cls,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ):
        """
        Get historical OHLCV data.
        """
        history = cls._get_cached_history(
            symbol,
            period,
            interval,
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

    @classmethod
    def get_historical_data(
        cls,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ):
        return cls._get_cached_history(
            symbol,
            period,
            interval,
        )

    @classmethod
    def get_ema(
        cls,
        symbol: str,
        period: int = 20,
        interval: str = "1d",
    ):
        """
        Calculate the latest EMA value.
        """
        history = cls.get_historical_data(
            symbol,
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

    @classmethod
    def get_rsi(
        cls,
        symbol: str,
        period: int = 14,
        interval: str = "1d",
    ):
        """
        Calculate the latest RSI value.
        """
        history = cls.get_historical_data(
            symbol,
            period="6mo",
            interval=interval,
        )

        if history.empty:
            return {
                "error": "No historical data found."
            }

        history["RSI"] = calculate_rsi(
            history,
            period,
        )

        latest = history.iloc[-1]

        rsi_value = round(float(latest["RSI"]), 2)

        if rsi_value > 70:
            signal = "Overbought"
        elif rsi_value < 30:
            signal = "Oversold"
        else:
            signal = "Neutral"

        return {
            "symbol": symbol,
            "indicator": f"RSI {period}",
            "current_price": round(float(latest["Close"]), 2),
            "rsi": rsi_value,
            "signal": signal,
        }

    @classmethod
    def get_macd(
        cls,
        symbol: str,
        interval: str = "1d",
    ):
        """
        Calculate MACD indicator.
        """
        history = cls.get_historical_data(
            symbol,
            period="6mo",
            interval=interval,
        )

        if history.empty:
            return {
                "error": "No historical data found."
            }

        macd, signal_line, histogram = calculate_macd(history)

        history["MACD"] = macd
        history["Signal"] = signal_line
        history["Histogram"] = histogram

        latest = history.iloc[-1]

        if latest["MACD"] > latest["Signal"]:
            trade_signal = "Bullish"
        elif latest["MACD"] < latest["Signal"]:
            trade_signal = "Bearish"
        else:
            trade_signal = "Neutral"

        return {
            "symbol": symbol,
            "current_price": round(float(latest["Close"]), 2),
            "macd": round(float(latest["MACD"]), 2),
            "signal_line": round(float(latest["Signal"]), 2),
            "histogram": round(float(latest["Histogram"]), 2),
            "signal": trade_signal,
        }