class ScoringEngine:

    INDICATOR_WEIGHTS = {
        "ema": 30,
        "rsi": 20,
        "macd": 30,
    }

    @staticmethod
    def calculate_score(indicators: dict):

        score = 0

        reasons = []

        # EMA
        if indicators["ema"]["signal"] == "Bullish":
            score += ScoringEngine.INDICATOR_WEIGHTS["ema"]
            reasons.append("Price above EMA")
        else:
            score -= ScoringEngine.INDICATOR_WEIGHTS["ema"]
            reasons.append("Price below EMA")

        # RSI
        if indicators["rsi"]["signal"] == "Oversold":
            score += ScoringEngine.INDICATOR_WEIGHTS["rsi"]
            reasons.append("RSI Oversold")

        elif indicators["rsi"]["signal"] == "Neutral":
            score += 10
            reasons.append("Healthy RSI")

        else:
            score -= ScoringEngine.INDICATOR_WEIGHTS["rsi"]
            reasons.append("RSI Overbought")

        # MACD
        if indicators["macd"]["signal"] == "Bullish":
            score += ScoringEngine.INDICATOR_WEIGHTS["macd"]
            reasons.append("MACD Bullish")

        else:
            score -= ScoringEngine.INDICATOR_WEIGHTS["macd"]
            reasons.append("MACD Bearish")

        return score, reasons