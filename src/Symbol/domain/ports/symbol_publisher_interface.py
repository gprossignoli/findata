from abc import ABCMeta, abstractmethod

from src.Symbol.domain.symbol import Symbol


class SymbolPublisherInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'publish_symbols') and
                callable(subclass.publish_symbols) and
                hasattr(subclass, 'publish_indexes') and
                callable(subclass.publish_indexes)) or NotImplemented

    @abstractmethod
    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        raise NotImplemented

    @abstractmethod
    def publish_indexes(self, indexes: tuple[Symbol, ...]) -> None:
        raise NotImplemented
