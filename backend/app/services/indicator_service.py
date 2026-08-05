from app.services.market_data import MarketDataService

from app.analysis.ema import calculate_ema
from app.analysis.rsi import calculate_rsi
from app.analysis.macd import calculate_macd


class IndicatorService:

    @staticmethod
    def get_all_indicators(symbol: str):

        history = MarketDataService.get_historical_data(symbol)

        if history.empty:
            return {
                "error": "No historical data found."
            }

        # EMA
        history["EMA"] = calculate_ema(history)

        latest = history.iloc[-1]

        ema = {
            "indicator": "EMA 20",
            "value": round(float(latest["EMA"]), 2),
            "signal": (
                "Bullish"
                if latest["Close"] > latest["EMA"]
                else "Bearish"
            ),
        }

        # RSI
        history["RSI"] = calculate_rsi(history)

        latest = history.iloc[-1]

        rsi_value = round(float(latest["RSI"]), 2)

        if rsi_value > 70:
            rsi_signal = "Overbought"
        elif rsi_value < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"

        rsi = {
            "indicator": "RSI 14",
            "value": rsi_value,
            "signal": rsi_signal,
        }

        # MACD
        macd_line, signal_line, histogram = calculate_macd(history)

        history["MACD"] = macd_line
        history["Signal"] = signal_line

        latest = history.iloc[-1]

        macd = {
            "indicator": "MACD",
            "value": round(float(latest["MACD"]), 2),
            "signal": (
                "Bullish"
                if latest["MACD"] > latest["Signal"]
                else "Bearish"
            ),
        }

        return {
            "symbol": symbol,
            "ema": ema,
            "rsi": rsi,
            "macd": macd,
        }