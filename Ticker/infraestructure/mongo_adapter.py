from datetime import datetime

from pymongo import MongoClient

from Ticker.domain import settings as st


class MongoAdapter:
    def __init__(self):
        st.logger.info("Connecting to mongodb database.")
        client = MongoClient(st.MONGO_HOST, int(st.MONGO_PORT))
        self.__db = client.findata

    def save_tickers(self, exchange: str, tickers: tuple[str]):
        collection = self.__db['exchanges']
        document = {
            "_id": exchange,
            "tickers": tickers,
            "date": datetime.utcnow()
        }

        collection.insert(document)
        pass



