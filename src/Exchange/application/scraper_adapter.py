import re
from bs4 import BeautifulSoup
import ujson

from src.Utils.exceptions import RepositoryException, DomainServiceException
from src.Exchange.domain.exchange import Exchange
from src.Exchange.domain.ports.exchange_service_interface import ExchangeServiceInterface
from src.Utils.http_request import HttpRequest, HttpRequestException
from src import settings as st


class ScraperAdapter(ExchangeServiceInterface):
    """
    This class is an adapter that implements the ExchangeService through
    the scrapping of the yahoo finance exchange components
    e.g. https://es.finance.yahoo.com/quote/^IBEX/components
    """

    def create_exchange_entity(self, ticker: str, symbols: tuple[str, ...]) -> Exchange:
        return Exchange(ticker=ticker, symbols=symbols)

    def fetch_stocks(self, exchange_tickers: tuple[str, ...]):
        st.logger.info("Fetching stocks for the following exchanges: {}".format(exchange_tickers))
        for ticker in exchange_tickers:
            tickers = self.__fetch_symbols(ticker)

            exchange = self.create_exchange_entity(ticker=ticker, symbols=tickers)
            st.logger.info("Saving the information of the exchange: {}".format(ticker))
            try:
                self.repository.save_exchange(exchange)
            except RepositoryException:
                raise DomainServiceException()

    @staticmethod
    def __fetch_symbols(ticker: str) -> tuple[str, ...]:
        try:
            req = HttpRequest(status_forcelist=[300, 301, 400, 401, 403, 404, 408, 500, 502, 503])\
                .get(url=f'https://es.finance.yahoo.com/quote/{ticker}/components', timeout=15)
        except HttpRequestException as e:
            raise DomainServiceException()

        soup = BeautifulSoup(req.content, features='lxml')
        script = soup.find("script", text=re.compile("root.App.main"))
        # It's necessary to use json, because the page uses react for loading the data.
        data = ujson.loads(re.search("root.App.main\s+=\s+(\{.*\})", str(script)).group(1))
        tickers_data = data['context']['dispatcher']['stores']['QuoteSummaryStore']['components']['components']
        tickers = tuple(tickers_data) if tickers_data is not None else tuple()
        return tickers
