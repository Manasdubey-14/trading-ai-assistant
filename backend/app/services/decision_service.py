from app.engine.decision import DecisionEngine


class DecisionService:

    @staticmethod
    def analyze(symbol: str):
        return DecisionEngine.analyze(symbol)