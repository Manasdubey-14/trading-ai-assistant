from sqlalchemy.orm import Session

from app.schemas.opportunity import Opportunity
from app.services.signal_service import SignalService


class OpportunityService:

    @staticmethod
    def calculate_score(signal):

        score = 0.0

        # Confidence contributes up to 50 points
        score += signal.confidence * 0.50

        # Trend
        if signal.trend == "Bullish" and signal.signal == "BUY":
            score += 20

        elif signal.trend == "Bearish" and signal.signal == "SELL":
            score += 20

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

        return round(score, 2), risk_reward

    @staticmethod
    def get_strength(score, signal):

        if signal == "BUY":

            if score >= 80:
                return "Strong Buy"

            elif score >= 60:
                return "Buy"

            else:
                return "Weak Buy"

        elif signal == "SELL":

            if score >= 80:
                return "Strong Sell"

            elif score >= 60:
                return "Sell"

            else:
                return "Weak Sell"

        return "Wait"

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