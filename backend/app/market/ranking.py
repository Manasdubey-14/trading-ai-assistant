from app.engine.opportunity_score import OpportunityScoreEngine


class RankingEngine:

    @staticmethod
    def rank(signals: list):

        return sorted(
            signals,
            key=lambda signal: OpportunityScoreEngine.calculate(signal)[0],
            reverse=True,
        )