from sqlalchemy.orm import Session
from app.engine.opportunity_score import OpportunityScoreEngine
from app.schemas.opportunity import Opportunity
from app.services.signal_service import SignalService


class OpportunityService:

    @staticmethod
    def calculate_score(signal):

         return OpportunityScoreEngine.calculate(signal)
    @staticmethod
    def get_strength(score, signal):

        if signal == "WAIT":
            return "Wait"

        if score >= 90:
            return (
                "Strong Buy"
                if signal == "BUY"
                else "Strong Sell"
            )

        if score >= 75:
            return (
                "Buy"
                if signal == "BUY"
                else "Sell"
            )

        if score >= 60:
            return (
                "Watch Buy"
                if signal == "BUY"
                else "Watch Sell"
            )

        return "Weak Signal"

    @staticmethod
    def get_top_opportunities(
        db: Session,
    ):

        signals = SignalService.get_latest_signals(
            db=db,
            limit=20,
        )

        opportunities = []

        for signal in signals:
            if signal.signal == "WAIT":
              continue

            score, risk_reward = (
                OpportunityService.calculate_score(signal)
            )

            strength = OpportunityService.get_strength(
                score,
                signal.signal,
            )

            opportunities.append(
                Opportunity(
                    rank=0,
                    symbol=signal.symbol,
                    signal=signal.signal,
                    confidence=signal.confidence,
                    score=score,
                    strength=strength,
                    trend=signal.trend,
                    entry=signal.entry,
                    target=signal.target,
                    stop_loss=signal.stop_loss,
                    risk_reward=(
                        round(risk_reward, 2)
                        if risk_reward is not None
                        else None
                    ),
                )
            )

        # Highest score first
        opportunities.sort(
            key=lambda opportunity: opportunity.score,
            reverse=True,
        )

        # Assign ranking
        for index, opportunity in enumerate(
            opportunities,
            start=1,
        ):
            opportunity.rank = index

        return opportunities