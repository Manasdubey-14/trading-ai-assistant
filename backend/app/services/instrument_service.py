from datetime import date
from pathlib import Path
import csv
import gzip

from app.market.instrument import Instrument


class InstrumentService:

    CACHE_DIR = Path("data/instruments")

    @classmethod
    def ensure_cache_directory(cls) -> None:
        cls.CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    @classmethod
    def save_instruments(
        cls,
        instruments: list[Instrument],
        filename: str = "instruments.csv",
    ) -> Path:

        cls.ensure_cache_directory()

        path = cls.CACHE_DIR / filename

        fieldnames = [
            "symbol",
            "name",
            "exchange",
            "segment",
            "instrument_type",
            "instrument_token",
            "expiry",
            "strike",
            "lot_size",
            "tick_size",
            "is_active",
        ]

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for instrument in instruments:

                writer.writerow({
                    "symbol": instrument.symbol,
                    "name": instrument.name or "",
                    "exchange": instrument.exchange or "",
                    "segment": instrument.segment or "",
                    "instrument_type": (
                        instrument.instrument_type or ""
                    ),
                    "instrument_token": (
                        instrument.instrument_token
                        if instrument.instrument_token is not None
                        else ""
                    ),
                    "expiry": (
                        instrument.expiry.isoformat()
                        if instrument.expiry
                        else ""
                    ),
                    "strike": (
                        instrument.strike
                        if instrument.strike is not None
                        else ""
                    ),
                    "lot_size": (
                        instrument.lot_size
                        if instrument.lot_size is not None
                        else ""
                    ),
                    "tick_size": (
                        instrument.tick_size
                        if instrument.tick_size is not None
                        else ""
                    ),
                    "is_active": instrument.is_active,
                })

        return path

    @classmethod
    def load_instruments(
        cls,
        filename: str = "instruments.csv",
    ) -> list[Instrument]:

        path = cls.CACHE_DIR / filename

        if not path.exists():
            return []

        instruments = []

        with path.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                expiry = None

                if row.get("expiry"):
                    expiry = date.fromisoformat(
                        row["expiry"]
                    )

                instruments.append(
                    Instrument(
                        symbol=row["symbol"],
                        name=row.get("name") or None,
                        exchange=row.get("exchange") or None,
                        segment=row.get("segment") or None,
                        instrument_type=(
                            row.get("instrument_type") or None
                        ),
                        instrument_token=(
                            int(row["instrument_token"])
                            if row.get("instrument_token")
                            else None
                        ),
                        expiry=expiry,
                        strike=(
                            float(row["strike"])
                            if row.get("strike")
                            else None
                        ),
                        lot_size=(
                            int(float(row["lot_size"]))
                            if row.get("lot_size")
                            else None
                        ),
                        tick_size=(
                            float(row["tick_size"])
                            if row.get("tick_size")
                            else None
                        ),
                        is_active=(
                            row.get("is_active", "").lower()
                            == "true"
                        ),
                    )
                )

        return instruments