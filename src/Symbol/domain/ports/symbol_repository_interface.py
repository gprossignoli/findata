from abc import ABCMeta, abstractmethod
from collections import namedtuple


class SymbolRepositoryInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'save_tickers') and
                callable(subclass.execute)) or NotImplemented

    @abstractmethod
    def fetch_symbols(self, symbols_tickers: tuple[str, ...]) -> tuple[namedtuple, ...]:
        """
        Fetches each symbol name, isin and historical data
        :param symbols_tickers: symbol's tickers from which get the info
        """
        raise NotImplemented