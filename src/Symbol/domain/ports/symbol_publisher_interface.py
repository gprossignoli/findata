from abc import ABCMeta, abstractmethod

from src.Symbol.domain.symbol import Symbol


class SymbolPublisherInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'publish_symbols') and
                callable(subclass.publish_symbols)) or NotImplemented

    @abstractmethod
    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        raise NotImplemented
