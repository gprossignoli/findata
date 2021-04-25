import time

import pandas as pd

from yfinance import Tickers as yf_tickers
from yfinance import Ticker as yf_ticker_info

from src.Symbol.domain.symbol import Symbol, SymbolInformation, Stock, IndexInformation
from src.Symbol.domain.ports.symbol_service_interface import SymbolServiceInterface
from src.Utils.exceptions import RepositoryException, DomainServiceException, PublisherException
from src import settings as st


class YFinanceAdapter(SymbolServiceInterface):

    def fetch_all_symbols(self, period: str = 'max', actions: bool = True) -> tuple[Symbol, ...]:
        """
        Fetch all symbol historic data from yahoo finance, using yfinance library
        and adds it to its info from the db
        :param period: time frame in which to collect the data
        :param actions: Download stock dividends and stock splits events?
        :return: information of each symbol
        """
        try:
            symbols_info = self.symbols_repository.get_symbols_info()
        except RepositoryException:
            raise DomainServiceException()
        symbols_tickers = [getattr(s, 'ticker') for s in symbols_info]

        st.logger.info("Getting historic of {} symbols with tickers: {}".format(len(symbols_tickers), symbols_tickers))

        symbols_history = self.__get_symbols_historic(symbols_tickers=tuple(symbols_tickers), period=period,
                                                      actions=actions)
        del symbols_tickers

        symbols_data = list()
        for symbol in symbols_info:
            symbols_data.append(self.create_symbol_entity(ticker=getattr(symbol, 'ticker'),
                                                          historical_data=symbols_history[getattr(symbol, 'ticker')],
                                                          name=getattr(symbol, 'name'), isin=getattr(symbol, 'isin'),
                                                          exchange=getattr(symbol, 'exchange')))
        return tuple(symbols_data)

    def fetch_all_symbols_info(self) -> None:
        exchanges = self.exchanges_repository.get_exchanges()
        for exchange in exchanges:
            if exchange.symbols:
                symbols = list(exchange.symbols)
                symbols.append(exchange.ticker)
                st.logger.info("Fetching symbols information for exchange: {}".format(exchange.ticker))
                self.__fetch_symbols_info(symbol_tickers=tuple(symbols), exchange_ticker=exchange.ticker)
        self.symbols_repository.clean_old_symbols()

    def fetch_indexes(self, period: str = 'max') -> tuple[Symbol, ...]:
        """
        Fetch all indexes historic data from yahoo finance, using yfinance library
        and adds it to its info from the db
        :param period: time frame in which to collect the data
        :return: information of each symbol
        """
        try:
            indexes_info = self.symbols_repository.get_indexes_info()
        except RepositoryException:
            raise DomainServiceException()
        indexes_tickers = [getattr(s, 'ticker') for s in indexes_info]

        st.logger.info("Getting historic of {} indexes with tickers: {}".format(len(indexes_tickers), indexes_tickers))

        indexes_history = self.__get_symbols_historic(symbols_tickers=tuple(indexes_tickers), period=period,
                                                      actions=False)
        del indexes_tickers

        indexes_data = list()
        for symbol in indexes_info:
            indexes_data.append(self.create_symbol_entity(ticker=getattr(symbol, 'ticker'),
                                                          historical_data=indexes_history[getattr(symbol, 'ticker')],
                                                          name=getattr(symbol, 'name')))
        return tuple(indexes_data)

    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        try:
            self.publisher.publish_symbols(symbols)
        except PublisherException:
            raise DomainServiceException()

    def publish_indexes(self, symbols: tuple[Symbol, ...]) -> None:
        try:
            self.publisher.publish_indexes(symbols)
        except PublisherException:
            raise DomainServiceException()

    def create_symbol_entity(self, ticker: str, historical_data: pd.DataFrame, name: str,
                             isin: str = None, exchange: str = None):
        # Holes gets filled with the previous data,
        # and it discards all the indexes until the first valid index
        historical_data = historical_data.fillna(method='ffill').dropna()
        if exchange is not None:
            return Stock(ticker=ticker, name=name, isin=isin, historical_data=historical_data, exchange=exchange)
        return Symbol(ticker=ticker, name=name, historical_data=historical_data)

    def __fetch_symbols_info(self, symbol_tickers: tuple[str, ...], exchange_ticker: str) -> None:
        """
        Fetch all the symbols info as name and isin using yfinance, and then stores it into db.
        """
        chunks = self.__get_chunks(symbol_tickers)
        for chunk in chunks:
            symbols = []
            st.logger.info("Fetching {} symbols info with tickers: {}".format(len(chunk), chunk))
            for ticker in chunk:
                try:
                    symbol_data = yf_ticker_info(ticker)
                    name = symbol_data.info.get('shortName')
                    if name is None:
                        name = symbol_data.info.get('longName', '-')
                    if ticker in st.exchanges:
                        if name == '-':
                            st.logger.info("Discarding symbol: {}".format(ticker))
                        else:
                            name = self.__format_name_field(name)
                            symbols.append(IndexInformation(ticker=ticker, name=name))
                    else:
                        isin = symbol_data.isin
                        if name == '-' or isin == '-':
                            st.logger.info("Discarding symbol: {}".format(ticker))
                        else:
                            name = self.__format_name_field(name)
                            symbols.append(SymbolInformation(ticker=ticker, name=name, isin=isin,
                                                             exchange=exchange_ticker))
                except Exception as e:
                    st.logger.exception(e)
                time.sleep(1)
            try:
                self.symbols_repository.save_symbols_info(symbols=tuple(symbols))
            except RepositoryException:
                raise DomainServiceException()

    @staticmethod
    def __format_name_field(name):
        name = name.lower()
        if "," in name and "s.a." in name:
            name = name.split(",")[0] + ", s.a."
        elif "s.a." in name:
            name = name.split("s")[0] + ", s.a."
        return name

    def __get_symbols_historic(self, symbols_tickers: tuple[str, ...], period: str = 'max',
                               actions: bool = True) -> dict[str, pd.DataFrame]:
        chunks = self.__get_chunks(symbols_tickers)

        hist_data = dict().fromkeys(symbols_tickers)
        for chunk in chunks:
            chunk_data = yf_tickers(tickers=list(chunk)).history(period=period, actions=actions)
            for symbol in chunk:
                hist_data[symbol] = chunk_data.filter(like=symbol, axis=1)
                hist_data[symbol].columns = hist_data[symbol].columns.droplevel(1)
                if actions:
                    try:
                        hist_data[symbol] = hist_data[symbol].drop(columns=['Stock Splits'])
                    except KeyError:
                        pass
        return hist_data

    @staticmethod
    def __get_chunks(symbols_tickers: tuple[str, ...]) -> tuple[tuple[str, ...]]:
        # Divides symbols_tickers in chunks for avoid to overload yahoo finance api
        chunk_len = 1000 if len(symbols_tickers) > 1000 else len(symbols_tickers)
        chunks = tuple(symbols_tickers[i:i + chunk_len] for i in range(0, len(symbols_tickers), chunk_len))
        return chunks
