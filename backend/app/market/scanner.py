from app.market.watchlist import Watchlist
from app.engine.decision import DecisionEngine
from app.market.ranking import RankingEngine


class MarketScanner:

    @staticmethod
    def scan():

        results = []

        for symbol in Watchlist.symbols:

            decision = DecisionEngine.analyze(symbol)

            results.append(decision)

        return RankingEngine.rank(results)