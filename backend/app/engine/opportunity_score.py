class OpportunityScoreEngine:

    @staticmethod
    def calculate(signal):
        score = 0.0

        # Confidence contribution
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

        score = min(score, 100)

        return round(score, 2), risk_reward