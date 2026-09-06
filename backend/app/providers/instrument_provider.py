from abc import ABC, abstractmethod

from app.market.instrument import Instrument


class InstrumentProvider(ABC):

    @abstractmethod
    def get_instruments(self) -> list[Instrument]:
        """
        Return the available market instruments.
        """
        raise NotImplementedError