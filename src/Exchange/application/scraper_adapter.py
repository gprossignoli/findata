import re
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import ujson

from src.Exchange.domain.exceptions import RepositoryException
from src.Exchange.domain.exchange import Exchange
from src.Exchange.domain.ports.exchange_repository_interface import ExchangeRepositoryInterface
from src.Exchange.domain.ports.exchange_service_interface import ExchangeServiceInterface
from src import settings as st


class ScraperException(Exception):
    pass


class ScraperAdapter(ExchangeServiceInterface):
    """
    This class is an adapter that implements the ExchangeService through
    the scrapping of the yahoo finance exchange components
    e.g. https://es.finance.yahoo.com/quote/^IBEX/components
    """

    def create_exchange_entity(self, ticker: str, symbols: tuple[str, ...]) -> Exchange:
        return Exchange(ticker=ticker, symbols=symbols)

    def fetch_stocks(self, exchanges: tuple[str, ...]):
        st.logger.info("Fetching stocks for the following exchanges: {}".format(exchanges))
        for exchange in exchanges:
            try:
                tickers = self.__fetch_symbols(exchange)
            except ScraperException:
                raise RepositoryException()

            exchange = self.create_exchange_entity(ticker=exchange, symbols=tickers)
            st.logger.info("Saving the information of the exchange: {}".format(exchange))
            try:
                self.repository.save_exchange(exchange)
            except RepositoryException as e:
                raise e

    @staticmethod
    def __fetch_symbols(exchange):
        try:
            req = requests.get(url=f'https://es.finance.yahoo.com/quote/{exchange}/components')
        except RequestException as e:
            st.logger.exception(e)
            raise ScraperException
        soup = BeautifulSoup(req.content, features='lxml')
        script = soup.find("script", text=re.compile("root.App.main"))
        # It's necessary to use json, because the page uses react for loading the data.
        data = ujson.loads(re.search("root.App.main\s+=\s+(\{.*\})", str(script)).group(1))
        tickers_data = data['context']['dispatcher']['stores']['QuoteSummaryStore']['components']['components']
        tickers = tuple(tickers_data) if tickers_data is not None else tuple()
        return tickers
