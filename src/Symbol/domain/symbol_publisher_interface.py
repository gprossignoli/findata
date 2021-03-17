from abc import ABCMeta


class SymbolPublisherInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        # TODO cambiar los metodos
        return (hasattr(subclass, 'fetch_stocks') and
                callable(subclass.fetch_stocks) and
                hasattr(subclass, 'create_exchange_entity') and
                callable(subclass.create_exchange_entity)) or NotImplemented

    def __init__(self):
        raise NotImplemented