import typing
from abc import ABCMeta, abstractmethod
from collections import namedtuple

from src.Symbol.domain.ports.symbol_service_interface import symbol_information as __symbol_information

symbol_info = __symbol_information


class SymbolRepositoryInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'save_symbols_info') and
                callable(subclass.save_symbols_info) and
                hasattr(subclass, 'get_symbols_info') and
                callable(subclass.get_symbols_info)
                ) or NotImplemented

    @abstractmethod
    def save_symbols_info(self, symbols: tuple[typing.NamedTuple, ...]):
        """
        Fetches each symbol name, isin and historical data
        :param symbols: Ticker, isin and name of each symbol
        """
        raise NotImplemented

    @abstractmethod
    def get_symbols_info(self) -> tuple:
        """
        Gets the symbols info from the db.
        :return: all symbols info.
        """
        raise NotImplemented
