from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session

from app.market.universe import MarketUniverse
from app.engine.decision import DecisionEngine
from app.market.ranking import RankingEngine
from app.services.signal_service import SignalService


class MarketScanner:

    MAX_WORKERS = 8

    @staticmethod
    def _analyze_symbol(symbol: str):
        try:
            return DecisionEngine.analyze(symbol)
        except Exception as exc:
            print(f"Scanner failed for {symbol}: {exc}")
            return None

    @staticmethod
    def scan():
        symbols = MarketUniverse.get_scan_symbols()
        results = []

        with ThreadPoolExecutor(
            max_workers=MarketScanner.MAX_WORKERS
        ) as executor:

            futures = {
                executor.submit(
                    MarketScanner._analyze_symbol,
                    symbol,
                ): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                decision = future.result()

                if decision is not None:
                    results.append(decision)

        return RankingEngine.rank(results)

    @staticmethod
    def scan_and_save(db: Session):
        results = MarketScanner.scan()

        for signal in results:
            SignalService.save_signal(
                db=db,
                signal=signal,
            )

        return results