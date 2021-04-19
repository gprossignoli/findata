import typing
from datetime import datetime, timedelta

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.Symbol.domain.ports.symbol_repository_interface import SymbolRepositoryInterface
from src.Symbol.domain.symbol import SymbolInformation, IndexInformation
from src.Utils.exceptions import RepositoryException
from src import settings as st


class MongoAdapter(SymbolRepositoryInterface):

    __db_client = None

    def __init__(self):
        self.__connect_to_db()
        self.collection = self.__db_client['findata']['symbols']

    def save_symbols_info(self, symbols: tuple[SymbolInformation, ...]):
        st.logger.info("Updating {} symbols info".format(len(symbols)))
        for symbol in symbols:
            doc_filter = {'_id': getattr(symbol, 'ticker')}
            doc_values = {"$set": {"isin": getattr(symbol, 'isin'),
                                   "name": getattr(symbol, 'name'),
                                   "exchange": getattr(symbol, 'exchange'),
                                   "date": datetime.utcnow()}}

            try:
                self.collection.update_one(filter=doc_filter, update=doc_values, upsert=True)
            except PyMongoError as e:
                st.logger.exception(e)
                st.logger.info("Symbol info for {} not updated due to an error".format(getattr(symbol, 'ticker')))
                continue

    def get_indexes_info(self) -> tuple[IndexInformation]:
        try:
            data = self.collection.find({"_id": {"$in": st.exchanges}})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

        return tuple(IndexInformation(ticker=d['_id'], isin=d['isin'], name=d['name']) for d in data)

    def get_symbols_info(self) -> tuple[SymbolInformation]:
        try:
            data = self.collection.find({})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

        return tuple(SymbolInformation(ticker=d['_id'], isin=d['isin'], name=d['name'], exchange=d['exchange']) for d in data
                     if d['_id'] not in st.exchanges)

    def clean_old_symbols(self) -> None:
        try:
            data = self.collection.find({})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

        date_limit = datetime.utcnow().date() - timedelta(days=5)
        symbols_to_delete = []
        for symbol in data:
            if symbol['date'].date() < date_limit:
                symbols_to_delete.append(symbol['_id'])

        if not symbols_to_delete:
            return
        try:
            st.logger.info("Cleaning symbols with tickers: {}".format(symbols_to_delete))
            self.collection.delete_many({"_id": {"$in": symbols_to_delete}})
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException

    @classmethod
    def __connect_to_db(cls):
        """
        Singleton method to initialize mongo database object
        """
        if cls.__db_client is None:
            try:
                st.logger.info("Connecting to mongodb database.")
                cls.__db_client = MongoClient(f'mongodb://{st.MONGO_HOST}:{st.MONGO_PORT}/', connect=False)
                # Forces a connection status check
                cls.__db_client.server_info()
            except PyMongoError as e:
                st.logger.exception(e)
                raise RepositoryException()
