from abc import ABCMeta, abstractmethod

from src.Exchange.domain.exchange import Exchange


class ExchangeRepositoryInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'save_tickers') and
                callable(subclass.execute)) or NotImplemented

    @abstractmethod
    def save_exchange(self, exchange: Exchange):
        """
        Saves the entity into the DB
        :param exchange: Exchange entity
        """
        raise NotImplemented

    @abstractmethod
    def get_exchanges(self) -> tuple[Exchange, ...]:
        """
        :return: All exchanges data from DB
        """
        raise NotImplemented
