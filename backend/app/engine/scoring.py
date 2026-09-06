class ScoringEngine:

    INDICATOR_WEIGHTS = {
        "ema": 30,
        "rsi": 20,
        "macd": 30,
    }

    @staticmethod
    def calculate_indicator_score(indicators: dict):

        score = 0
        reasons = []

        # EMA
        if indicators["ema"]["signal"] == "Bullish":
            score += 30
            reasons.append("Price above EMA")
        else:
            score -= 30
            reasons.append("Price below EMA")

        # RSI
        if indicators["rsi"]["signal"] == "Oversold":
            score += 20
            reasons.append("RSI Oversold")
        elif indicators["rsi"]["signal"] == "Neutral":
            score += 10
            reasons.append("Healthy RSI")
        else:
            score -= 20
            reasons.append("RSI Overbought")

        # MACD
        if indicators["macd"]["signal"] == "Bullish":
            score += 30
            reasons.append("MACD Bullish")
        else:
            score -= 30
            reasons.append("MACD Bearish")

        return score, reasons

    @staticmethod
    def calculate_opportunity_score(signal):

        score = 0.0

        # Confidence (0–50)
        score += signal.confidence * 0.50

        # Signal quality
        if signal.signal in ("BUY", "SELL"):
            score += 20

        # Trend confirmation
        if signal.signal == "BUY" and signal.trend == "Bullish":
            score += 10
        elif signal.signal == "SELL" and signal.trend == "Bearish":
            score += 10

        # Risk / Reward
        risk_reward = None

        if (
            signal.entry is not None
            and signal.stop_loss is not None
            and signal.target is not None
        ):

            risk = abs(signal.entry - signal.stop_loss)
            reward = abs(signal.target - signal.entry)

            if risk > 0:

                risk_reward = reward / risk

                if risk_reward >= 3:
                    score += 20
                elif risk_reward >= 2:
                    score += 15
                elif risk_reward >= 1.5:
                    score += 10

        return min(round(score, 2), 100), risk_reward