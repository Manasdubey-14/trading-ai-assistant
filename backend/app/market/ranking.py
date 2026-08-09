class RankingEngine:

    @staticmethod
    def rank(signals: list):

        return sorted(
            signals,
            key=lambda signal: signal.confidence,
            reverse=True,
        )