from datetime import date, datetime, time
from zoneinfo import ZoneInfo


class TradingCalendarService:

    MARKET_TIMEZONE = ZoneInfo("Asia/Kolkata")

    MARKET_OPEN = time(9, 15)

    EQUITY_CLOSE = time(15, 30)

    FNO_CLOSE = time(15, 40)

    EQUITY_FNO_CONTINUOUS_CLOSE = time(15, 15)

    CAS_START = time(15, 15)

    CAS_END = time(15, 35)

    # NSE holidays for 2026
    NSE_HOLIDAYS = {
        date(2026, 1, 26),
        date(2026, 3, 3),
        date(2026, 3, 26),
        date(2026, 3, 31),
        date(2026, 4, 3),
        date(2026, 4, 14),
        date(2026, 5, 1),
        date(2026, 5, 27),
        date(2026, 6, 26),
        date(2026, 9, 14),
        date(2026, 10, 2),
        date(2026, 10, 20),
        date(2026, 11, 9),
        date(2026, 11, 10),
        date(2026, 11, 24),
        date(2026, 12, 25),
    }

    @staticmethod
    def get_day_info(requested_date: date):

        day_name = requested_date.strftime("%A")

        if requested_date.weekday() >= 5:

            return {
                "date": requested_date,
                "is_trading_day": False,
                "day_name": day_name,
                "reason": "Weekend",
            }

        if requested_date in TradingCalendarService.NSE_HOLIDAYS:

            return {
                "date": requested_date,
                "is_trading_day": False,
                "day_name": day_name,
                "reason": "NSE Market Holiday",
            }

        return {
            "date": requested_date,
            "is_trading_day": True,
            "day_name": day_name,
            "reason": "Regular trading day",
        }

    @staticmethod
    def get_session_status(segment: str = "EQUITY"):

        now = datetime.now(
            TradingCalendarService.MARKET_TIMEZONE
        )

        calendar = TradingCalendarService.get_day_info(
            now.date()
        )

        if not calendar["is_trading_day"]:

            return {
                "segment": segment,
                "status": "CLOSED",
                "reason": calendar["reason"],
            }

        current_time = now.time()

        if segment == "EQUITY":

            if (
                TradingCalendarService.MARKET_OPEN
                <= current_time
                <= TradingCalendarService.EQUITY_CLOSE
            ):
                return {
                    "segment": segment,
                    "status": "REGULAR_TRADING",
                    "reason": "Equity market is open",
                }

        elif segment == "EQUITY_FNO":

            if (
                TradingCalendarService.MARKET_OPEN
                <= current_time
                < TradingCalendarService.EQUITY_FNO_CONTINUOUS_CLOSE
            ):
                return {
                    "segment": segment,
                    "status": "REGULAR_TRADING",
                    "reason": "Continuous trading session",
                }

            if (
                TradingCalendarService.CAS_START
                <= current_time
                <= TradingCalendarService.CAS_END
            ):
                return {
                    "segment": segment,
                    "status": "CAS",
                    "reason": "Closing Auction Session",
                }

        elif segment == "FNO":

            if (
                TradingCalendarService.MARKET_OPEN
                <= current_time
                <= TradingCalendarService.FNO_CLOSE
            ):
                return {
                    "segment": segment,
                    "status": "REGULAR_TRADING",
                    "reason": "F&O market is open",
                }

        return {
            "segment": segment,
            "status": "CLOSED",
            "reason": "Outside trading hours",
        }

    @staticmethod
    def is_market_open(segment: str = "EQUITY"):

        session = TradingCalendarService.get_session_status(
            segment
        )

        return session["status"] == "REGULAR_TRADING"