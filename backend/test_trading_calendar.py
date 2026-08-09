from app.services.trading_calendar_service import (
    TradingCalendarService,
)


segments = [
    "EQUITY",
    "EQUITY_FNO",
    "FNO",
]


for segment in segments:

    result = TradingCalendarService.get_session_status(
        segment
    )

    print(
        f"{segment}: "
        f"{result['status']} - "
        f"{result['reason']}"
    )