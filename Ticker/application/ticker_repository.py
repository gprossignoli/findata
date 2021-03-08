from Ticker.infraestructure.mongo_adapter import MongoAdapter
from Ticker.infraestructure.scraper_adapter import ScraperAdapter


class TickerRepository:
    def __init__(self):
        self.__mongo_adapter = None
        self.__scraper_adapter = None

    def obtain_all_tickers(self, exchange: str) -> tuple[str]:
        """
        Obtains all tickers that compounds a stock exchange.

        :param exchange: Stock exchange from which we want to get the tickers.
        :return: Tickers that compounds the specified stock exchange.
        """

        self.__scraper_adapter = ScraperAdapter()
        tickers = self.__scraper_adapter.obtain_tickers(exchange)
        return tickers

    def store_tickers(self, exchange: str, tickers: tuple[str]):
        self.__mongo_adapter = MongoAdapter()
        self.__mongo_adapter.save_tickers(exchange=exchange, tickers=tickers)
