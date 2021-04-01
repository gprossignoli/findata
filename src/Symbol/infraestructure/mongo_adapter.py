import typing
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.Utils.exceptions import RepositoryException
from src.Symbol.domain.ports.symbol_repository_interface import SymbolRepositoryInterface, symbol_info
from src import settings as st


class MongoAdapter(SymbolRepositoryInterface):
    __db_client = None

    def __init__(self):
        self.__connect_to_db()

    def save_symbols_info(self, symbols: tuple[typing.NamedTuple, ...]):
        collection = self.__db_client['findata']['symbols']
        st.logger.info("Updating {} symbols info".format(len(symbols)))
        for symbol in symbols:
            doc_filter = {'_id': getattr(symbol, 'ticker')}
            doc_values = {"$set": {"isin": getattr(symbol, 'isin'),
                                   "name": getattr(symbol, 'name'),
                                   "date": datetime.utcnow()}}

            try:
                collection.update_one(filter=doc_filter, update=doc_values, upsert=True)
            except PyMongoError as e:
                st.logger.exception(e)
                st.logger.info("Symbol info for {} not updated due to an error".format(getattr(symbol, 'ticker')))
                continue

    def get_symbols_info(self) -> tuple[symbol_info, ...]:
        collection = self.__db_client['findata']['symbols']
        try:
            data = collection.find({})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

        return tuple(symbol_info(ticker=d['_id'], isin=d['isin'], name=d['name']) for d in data)

    @classmethod
    def __connect_to_db(cls):
        """
        Singleton method to initialize mongo database object
        """
        if cls.__db_client is None:
            try:
                st.logger.info("Connecting to mongodb database.")
                cls.__db_client = MongoClient(f'mongodb://{st.MONGO_HOST}:{st.MONGO_PORT}/')
                # Forces a connection status check
                cls.__db_client.server_info()
            except PyMongoError as e:
                st.logger.exception(e)
                raise RepositoryException()
