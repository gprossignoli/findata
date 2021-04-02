from abc import ABCMeta, abstractmethod
from collections import namedtuple

from pandas import DataFrame

from src.Exchange.domain.ports.exchange_repository_interface import ExchangeRepositoryInterface
from src.Symbol.domain.ports.symbol_publisher_interface import SymbolPublisherInterface
from src.Symbol.domain.ports.symbol_repository_interface import SymbolRepositoryInterface
from src.Symbol.domain.symbol import Symbol


class SymbolServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'fetch_all_symbols') and
                callable(subclass.fetch_all_symbols) and
                hasattr(subclass, 'publish_symbols') and
                callable(subclass.publish_symbols) and
                hasattr(subclass, 'create_symbol_entity') and
                callable(subclass.create_symbol_entity) and
                hasattr(subclass, 'fetch_all_symbols_info') and
                callable(subclass.fetch_all_symbols_info)) or NotImplemented

    def __init__(self, symbols_repository: SymbolRepositoryInterface, exchanges_repository: ExchangeRepositoryInterface,
                 publisher: SymbolPublisherInterface = None):
        self.publisher = publisher
        self.symbols_repository = symbols_repository
        self.exchanges_repository = exchanges_repository

    @abstractmethod
    def fetch_all_symbols(self) -> tuple[Symbol, ...]:
        """
        Fetch all symbols data and returns it as Symbol Entities.

        :return: Symbols entities.
        """
        raise NotImplemented

    @abstractmethod
    def fetch_all_symbols_info(self) -> None:
        """
        Fetch all symbols basic info and then saves it into db.
        """
        raise NotImplemented

    @abstractmethod
    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        """
        Publish the symbols entities as event message.

        :param symbols: Symbols entities
        """

        raise NotImplemented

    @abstractmethod
    def create_symbol_entity(self, ticker: str, historical_data: DataFrame, name: str = None,
                             isin: str = None) -> Symbol:
        raise NotImplemented
