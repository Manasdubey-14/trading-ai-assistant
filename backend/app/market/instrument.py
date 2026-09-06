from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Instrument:
    symbol: str
    name: Optional[str] = None

    exchange: Optional[str] = None
    segment: Optional[str] = None
    instrument_type: Optional[str] = None

    instrument_token: Optional[int] = None

    expiry: Optional[date] = None
    strike: Optional[float] = None

    lot_size: Optional[int] = None
    tick_size: Optional[float] = None

    is_active: bool = True