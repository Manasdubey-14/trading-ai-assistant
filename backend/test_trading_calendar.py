from datetime import date

from app.services.trading_calendar_service import (
    TradingCalendarService,
)


dates = [
    date(2026, 8, 7),   # Friday
    date(2026, 8, 8),   # Saturday
    date(2026, 8, 9),   # Sunday
    date(2026, 8, 15),  # Independence Day
    date(2026, 10, 2),  # Gandhi Jayanti
]


for requested_date in dates:

    result = TradingCalendarService.get_day_info(
        requested_date
    )

    print(result)