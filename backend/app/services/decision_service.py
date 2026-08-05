from app.services.indicator_service import IndicatorService

class DecisionService:

    @staticmethod
    def analyze(symbol: str):

        indicators = IndicatorService.get_all_indicators(symbol)

        ema = indicators["ema"]

        rsi = indicators["rsi"]

        macd = indicators["macd"]
        score = 0

        reasons = []

        # EMA
        if ema["signal"] == "Bullish":
            score += 30
            reasons.append("Price is above EMA")

        else:
            score -= 30
            reasons.append("Price is below EMA")

        # RSI
        if rsi["signal"] == "Oversold":
            score += 20
            reasons.append("RSI indicates oversold conditions")

        elif rsi["signal"] == "Neutral":
            score += 10
            reasons.append("RSI shows healthy momentum")

        else:
            score -= 20
            reasons.append("RSI indicates overbought conditions")

        # MACD
        if macd["signal"] == "Bullish":
            score += 30
            reasons.append("MACD bullish crossover")

        else:
            score -= 30
            reasons.append("MACD bearish crossover")

        # Final Decision
        if score >= 50:
            signal = "BUY"
            trend = "Bullish"

        elif score <= -50:
            signal = "SELL"
            trend = "Bearish"

        else:
            signal = "WAIT"
            trend = "Sideways"

        confidence = min(abs(score), 100)

        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence,
            "trend": trend,
            "reasons": reasons,
        }