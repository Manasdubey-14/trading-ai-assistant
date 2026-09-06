from app.market.instrument import Instrument
from app.providers.instrument_provider import InstrumentProvider
from app.providers.local_instrument_provider import LocalInstrumentProvider


class MarketUniverse:

    _provider: InstrumentProvider = LocalInstrumentProvider()

    @classmethod
    def set_provider(
        cls,
        provider: InstrumentProvider,
    ) -> None:
        cls._provider = provider

    @classmethod
    def get_all(cls) -> list[Instrument]:
        return cls._provider.get_instruments()

    @classmethod
    def get_equities(cls) -> list[Instrument]:
        return [
            instrument
            for instrument in cls.get_all()
            if instrument.instrument_type == "EQ"
        ]

    @classmethod
    def get_scan_symbols(cls) -> list[str]:
        return [
            instrument.symbol
            for instrument in cls.get_equities()
            if instrument.is_active
        ]

    @classmethod
    def find_symbol(
        cls,
        symbol: str,
    ) -> Instrument | None:

        normalized = symbol.strip().upper()

        for instrument in cls.get_all():

            if instrument.symbol.upper() == normalized:
                return instrument

        return None