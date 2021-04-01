from abc import ABCMeta, abstractmethod

from src.Exchange.domain.exchange import Exchange
from src.Exchange.domain.ports.exchange_repository_interface import ExchangeRepositoryInterface


class ExchangeServiceInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'fetch_stocks') and
                callable(subclass.fetch_stocks) and
                hasattr(subclass, 'create_exchange_entity') and
                callable(subclass.create_exchange_entity)) or NotImplemented

    def __init__(self, repository: ExchangeRepositoryInterface):
        self.repository = repository

    @abstractmethod
    def fetch_stocks(self, exchanges: tuple[str, ...]):
        """
        Obtains all tickers that compounds a stock exchange.

        :param exchanges: Stock exchanges from which we want to get the tickers.
        :return: Tickers that compounds the specified stock exchange.
        """
        raise NotImplemented

    @abstractmethod
    def create_exchange_entity(self, ticker: str, symbols: tuple[str, ...]) -> Exchange:
        raise NotImplemented
