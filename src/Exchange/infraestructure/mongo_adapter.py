from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src import settings as st
from src.Utils.exceptions import RepositoryException
from src.Exchange.domain.exchange import Exchange

from src.Exchange.domain.ports.exchange_repository_interface import ExchangeRepositoryInterface


class MongoAdapter(ExchangeRepositoryInterface):
    __db_client = None

    def __init__(self):
        self.__connect_to_db()
        self.collection = self.__db_client['findata']['exchanges']

    def save_exchange(self, exchange: Exchange) -> None:
        doc_filter = {'_id': exchange.ticker}
        doc_values = {"$set": {"tickers": exchange.symbols,
                               "date": datetime.utcnow()}}

        try:
            self.collection.update_one(filter=doc_filter, update=doc_values, upsert=True)
        except PyMongoError as e:
            st.logger.exception(e)
            raise RepositoryException()
        st.logger.info(f'{exchange.ticker} updated')

    def get_exchanges(self) -> tuple[Exchange, ...]:
        data = self.collection.find({})
        exchanges = [Exchange(ticker=d['_id'], symbols=d['tickers']) for d in data]
        return tuple(exchanges)

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
