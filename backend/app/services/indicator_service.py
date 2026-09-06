from app.services.market_data import MarketDataService
from app.schemas.evidence import TechnicalEvidence
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
            "current_price": round(
                float(latest["Close"]),
                2,
            ),
            "ema": ema,
            "rsi": rsi,
            "macd": macd,
        }

    @staticmethod
    def get_technical_evidence(symbol: str):

        indicators = IndicatorService.get_all_indicators(symbol)

        if "error" in indicators:
            return indicators

        ema_signal = indicators["ema"]["signal"]
        rsi_signal = indicators["rsi"]["signal"]
        macd_signal = indicators["macd"]["signal"]

        # Technical direction
        bullish_points = 0.0
        bearish_points = 0.0

        if ema_signal == "Bullish":
            bullish_points += 30
        else:
            bearish_points += 30

        if macd_signal == "Bullish":
            bullish_points += 30
        else:
            bearish_points += 30

        if rsi_signal == "Oversold":
            bullish_points += 20
        elif rsi_signal == "Overbought":
            bearish_points += 20
        else:
            # Neutral RSI does not strongly favor either direction.
            bullish_points += 10
            bearish_points += 10

        technical_score = bullish_points - bearish_points

        if technical_score > 0:
            direction = "Bullish"
        elif technical_score < 0:
            direction = "Bearish"
        else:
            direction = "Neutral"

        strength = round(abs(technical_score) / 80, 2)

        return TechnicalEvidence(
            direction=direction,
            strength=strength,
            ema_signal=ema_signal,
            rsi_signal=rsi_signal,
            macd_signal=macd_signal,
        )