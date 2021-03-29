from abc import ABCMeta, abstractmethod

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
                callable(subclass.publish_symbols)) or NotImplemented

    def __init__(self, publisher: SymbolPublisherInterface, symbols_repository: SymbolRepositoryInterface,
                 exchanges_repository: ExchangeRepositoryInterface):
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
    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        """
        Publish the symbols entities as event message.

        :param symbols: Symbols entities
        """

        raise NotImplemented
