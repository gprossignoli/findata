import typing
from abc import ABCMeta, abstractmethod

from src.Symbol.domain.symbol import SymbolInformation


class SymbolRepositoryInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'save_symbols_info') and
                callable(subclass.save_symbols_info) and
                hasattr(subclass, 'get_indexes_info') and
                callable(subclass.get_indexes_info) and
                hasattr(subclass, 'get_symbols_info') and
                callable(subclass.get_symbols_info) and
                hasattr(subclass, 'clean_old_symbols') and
                callable(subclass.clean_old_symbols)
                ) or NotImplemented

    @abstractmethod
    def save_symbols_info(self, symbols: tuple[SymbolInformation, ...]):
        """
        Fetches each symbol name, isin and historical data
        :param symbols: Ticker, isin and name of each symbol
        """
        raise NotImplemented

    @abstractmethod
    def get_indexes_info(self) -> tuple[SymbolInformation]:
        """
        Gets the indexes info from the db.
        :return: all symbols info.
        """
        raise NotImplemented

    @abstractmethod
    def get_symbols_info(self) -> tuple[SymbolInformation]:
        """
        Gets the symbols info from the db.
        :return: all symbols info.
        """
        raise NotImplemented

    @abstractmethod
    def clean_old_symbols(self) -> None:
        """
        Finds symbols not updated and cleans it.
        """
        raise NotImplemented
