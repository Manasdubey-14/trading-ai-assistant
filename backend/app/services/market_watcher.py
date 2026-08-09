from app.services.decision_service import DecisionService


class MarketWatcher:

    WATCHLIST = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
    ]

    @staticmethod
    def analyze_watchlist():

        results = []

        for symbol in MarketWatcher.WATCHLIST:

            analysis = DecisionService.analyze(symbol)

            results.append(analysis)

        return results