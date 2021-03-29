import time
from collections import namedtuple

import pandas as pd

from src.Symbol.domain.symbol import Symbol
from src.Symbol.infraestructure.rabbitmq_publisher_adapter import RabbitException
from yfinance import Tickers as yf_tickers
from yfinance import Ticker as yf_ticker_info

from src.Symbol.domain.ports.symbol_service_interface import SymbolServiceInterface
from src import settings as st


symbol_information = namedtuple("symbol_information", "ticker, history, name, isin")


class YFinanceAdapter(SymbolServiceInterface):

    def fetch_all_symbols(self) -> tuple[Symbol, ...]:
        symbols = []

        exchanges = self.exchanges_repository.get_exchanges()
        for exchange in exchanges:
            if exchange.symbols:
                st.logger.info("Fetching symbols for exchange: {}".format(exchange.ticker))
                symbols_info = self.__fetch_symbols(exchange.symbols)
                for symbol_info in symbols_info:
                    if symbol_info.isin == '-' or symbol_info.name == 'Name_Unknown':
                        st.logger.info("Discarding symbol: {}".format(symbol_info.ticker))
                        continue
                    # holes gets filled with the previous data,
                    # and it discards all the indexes until the first valid index
                    historical_data = symbol_info.history.fillna(method='ffill').dropna()
                    symbols.append(self.create_symbol_entity(ticker=symbol_info.ticker,
                                                               name=symbol_info.name,
                                                               isin=symbol_info.isin,
                                                               historical_data=historical_data))

                # 5 secs between executions to avoid overloading yahoo finance api
                time.sleep(5)
        return tuple(symbols)

    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        try:
            self.publisher.publish_symbols(symbols)
        except RabbitException:
            pass

    def create_symbol_entity(self, ticker: str, historical_data: pd.DataFrame, name: str = None, isin: str = None):
        return Symbol(ticker=ticker, name=name, isin=isin, historical_data=historical_data)

    def __fetch_symbols(self, symbols_tickers: tuple[str, ...], period: str = 'max',
                        actions: bool = False) -> tuple[symbol_information, ...]:
        """
        Fetch all symbol data from yahoo finance, using yfinance library
        :param symbols_tickers: symbol's tickers from which get the info
        :param period: time frame in which to collect the data
        :param actions: Download stock dividends and stock splits events?
        :return: information of each symbol
        """
        st.logger.info("Getting historic of symbols: {}".format(symbols_tickers))
        symbols_history = self.__get_symbols_historic(symbols_tickers=symbols_tickers, period=period,
                                                      actions=actions)

        symbols_data = list()
        for symbol in symbols_tickers:
            isin, name = self.__get_symbol_info(symbol)
            symbols_data.append(symbol_information(ticker=symbol,
                                                   history=symbols_history[symbol],
                                                   name=name, isin=isin))
            time.sleep(1)
        return tuple(symbols_data)

    # todo
    def __get_symbol_info(self, symbol):
        symbol_info = yf_ticker_info(symbol)
        name = symbol_info.info.get('shortName')
        if name is None:
            name = symbol_info.info.get('longName', 'Name_Unknown')
        name = name.split(',')[0]
        isin = symbol_info.isin
        return isin, name

    @staticmethod
    def __get_symbols_historic(symbols_tickers, period: str = 'max',
                               actions: bool = False) -> dict[str, pd.DataFrame]:
        # Divides symbols_tickers in chunks for avoid to overload yahoo finance api
        chunk_len = 1000 if len(symbols_tickers) > 1000 else len(symbols_tickers)
        chunks = [symbols_tickers[i:i+chunk_len] for i in range(0, len(symbols_tickers), chunk_len)]

        hist_data = dict().fromkeys(symbols_tickers)
        for chunk in chunks:
            chunk_data = yf_tickers(tickers=chunk).history(period=period, actions=actions)
            for symbol in chunk:
                hist_data[symbol] = chunk_data.filter(like=symbol, axis=1)
                hist_data[symbol].columns = hist_data[symbol].columns.droplevel(1)
        return hist_data

