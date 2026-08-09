from app.market.scanner import MarketScanner
from app.services.trading_calendar_service import (
    TradingCalendarService,
)


class MarketWatcher:

    @staticmethod
    def run_once(
        segment: str = "EQUITY_FNO",
    ):

        session = TradingCalendarService.get_session_status(
            segment
        )

        print(
            f"Market session: "
            f"{session['status']} "
            f"({session['reason']})"
        )

        # Market closed
        if session["status"] == "CLOSED":

            return []

        # Closing Auction Session
        if session["status"] == "CAS":

            print(
                "CAS active. "
                "Normal market scanner paused."
            )

            return []

        # Regular trading
        print("Market open. Scanning market...")

        results = MarketScanner.scan()

        return results