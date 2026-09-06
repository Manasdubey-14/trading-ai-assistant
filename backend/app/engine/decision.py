from app.services.indicator_service import IndicatorService
from app.schemas.signal import SignalResponse
from app.engine.risk import RiskEngine
from app.engine.scoring import ScoringEngine
from app.services.market_data import MarketDataService
class DecisionEngine:

    @staticmethod
    def analyze(symbol: str):

        indicators = IndicatorService.get_all_indicators(symbol)
        

        

       
        score, reasons = ScoringEngine.calculate_indicator_score(
            indicators
        )

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
        trade_plan = RiskEngine.calculate_trade_plan(
            current_price=indicators["current_price"],
            signal=signal,
        )

        return SignalResponse(
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            trend=trend,

            entry=trade_plan["entry"],
            stop_loss=trade_plan["stop_loss"],
            target=trade_plan["target"],
            risk_reward=trade_plan["risk_reward"],

            reasons=reasons,
        )