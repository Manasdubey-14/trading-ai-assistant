import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from sqlalchemy.orm import Session

from app.market.universe import MarketUniverse
from app.engine.decision import DecisionEngine
from app.market.ranking import RankingEngine
from app.services.signal_service import SignalService
from app.services.market_data import MarketDataService


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
        start_time = time.perf_counter()

        symbols = MarketUniverse.get_scan_symbols()
        MarketDataService.preload_history(
            symbols,
            period="6mo",
            interval="1d",
        )
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

        elapsed = time.perf_counter() - start_time

        print(
            f"[Scanner] "
            f"Scanned={len(symbols)} "
            f"Successful={len(results)} "
            f"Failed={len(symbols) - len(results)} "
            f"Time={elapsed:.2f}s"
        )

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