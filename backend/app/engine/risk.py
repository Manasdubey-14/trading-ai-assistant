class RiskEngine:

    RISK_REWARD_RATIO = 2.0

    @staticmethod
    def calculate_trade_plan(
        current_price: float,
        signal: str,
    ):

        if signal == "BUY":

            stop_loss = current_price * 0.99

            target = current_price + (
                (current_price - stop_loss)
                * RiskEngine.RISK_REWARD_RATIO
            )

        elif signal == "SELL":

            stop_loss = current_price * 1.01

            target = current_price - (
                (stop_loss - current_price)
                * RiskEngine.RISK_REWARD_RATIO
            )

        else:

            stop_loss = None
            target = None

        return {
            "entry": round(current_price, 2),
            "stop_loss": round(stop_loss, 2) if stop_loss else None,
            "target": round(target, 2) if target else None,
            "risk_reward": RiskEngine.RISK_REWARD_RATIO,
        }