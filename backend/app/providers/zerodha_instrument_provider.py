import csv
import gzip
import io
from datetime import date
from typing import Optional

import requests

from app.market.instrument import Instrument
from app.providers.instrument_provider import InstrumentProvider


class ZerodhaInstrumentProvider(InstrumentProvider):
    """
    Downloads and normalizes the Zerodha Kite instrument master.

    This provider only handles instrument metadata.
    It does not place orders or require broker execution logic.
    """

    INSTRUMENT_URL = (
        "https://api.kite.trade/instruments"
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.timeout = timeout

    def get_instruments(self) -> list[Instrument]:
        response = requests.get(
            self.INSTRUMENT_URL,
            timeout=self.timeout,
        )

        response.raise_for_status()

        raw_data = gzip.decompress(
            response.content
        )

        text = raw_data.decode(
            "utf-8",
            errors="replace",
        )

        reader = csv.DictReader(
            io.StringIO(text)
        )

        instruments = []

        for row in reader:
            expiry = None

            if row.get("expiry"):
                try:
                    expiry = date.fromisoformat(
                        row["expiry"]
                    )
                except ValueError:
                    expiry = None

            strike = None

            if row.get("strike"):
                try:
                    strike = float(row["strike"])
                except ValueError:
                    strike = None

            lot_size = None

            if row.get("lot_size"):
                try:
                    lot_size = int(
                        float(row["lot_size"])
                    )
                except ValueError:
                    lot_size = None

            tick_size = None

            if row.get("tick_size"):
                try:
                    tick_size = float(
                        row["tick_size"]
                    )
                except ValueError:
                    tick_size = None

            instrument_token = None

            if row.get("instrument_token"):
                try:
                    instrument_token = int(
                        row["instrument_token"]
                    )
                except ValueError:
                    instrument_token = None

            instruments.append(
                Instrument(
                    symbol=row.get(
                        "tradingsymbol",
                        "",
                    ),
                    name=row.get("name") or None,
                    exchange=row.get("exchange") or None,
                    segment=row.get("segment") or None,
                    instrument_type=(
                        row.get("instrument_type")
                        or None
                    ),
                    instrument_token=instrument_token,
                    expiry=expiry,
                    strike=strike,
                    lot_size=lot_size,
                    tick_size=tick_size,
                    is_active=True,
                )
            )

        return instruments