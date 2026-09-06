import asyncio

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.services.position_service import PositionService
from app.services.trading_calendar_service import (
    TradingCalendarService,
)


class PaperTradingMonitor:

    INTERVAL_SECONDS = 60

    @staticmethod
    def run_once():

        db: Session = SessionLocal()

        try:
            session = (
                TradingCalendarService.get_session_status(
                    "EQUITY_FNO"
                )
            )

            status = session.get("status")

            print(
                f"[Paper Monitor] "
                f"Market session: {status}"
            )

            if status in {"CLOSED", "CAS"}:
                print(
                    "[Paper Monitor] "
                    "Market not in regular trading. "
                    "Skipping."
                )
                return {
                    "status": "SKIPPED",
                    "reason": session.get("reason"),
                }

            result = (
                PositionService.monitor_positions(db)
            )

            print(
                "[Paper Monitor] "
                f"Updated: "
                f"{len(result.get('updated_positions', []))} "
                f"positions | "
                f"Triggered: "
                f"{len(result.get('triggered_positions', []))}"
            )

            return result

        except Exception as exc:

            print(
                f"[Paper Monitor] Error: {exc}"
            )

            return {
                "status": "ERROR",
                "error": str(exc),
            }

        finally:
            db.close()

    @classmethod
    async def run_loop(cls):

        print(
            "[Paper Monitor] "
            "Background monitor started."
        )

        while True:

            try:
                cls.run_once()

            except Exception as exc:
                print(
                    f"[Paper Monitor] "
                    f"Loop error: {exc}"
                )

            await asyncio.sleep(
                cls.INTERVAL_SECONDS
            )