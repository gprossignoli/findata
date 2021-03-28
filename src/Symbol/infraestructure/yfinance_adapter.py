import time
from collections import namedtuple

import pandas as pandas
from yfinance import Tickers as yf_tickers
from yfinance import Ticker as yf_ticker_info

from src.Symbol.domain.ports.symbol_repository_interface import SymbolRepositoryInterface
from src import settings as st


class YFinanceAdapter(SymbolRepositoryInterface):
    symbol_information = namedtuple("symbol_information", "ticker, history, name, isin")

    @classmethod
    def fetch_symbols(cls, symbols_tickers: tuple[str, ...], period: str = 'max',
                      actions: bool = False) -> tuple[symbol_information, ...]:
        """
        Fetch all symbol data from yahoo finance, using yfinance library
        :param symbols_tickers: symbol's tickers from which get the info
        :param period: time frame in which to collect the data
        :param actions: Download stock dividends and stock splits events?
        :return: information of each symbol
        """
        st.logger.info("Getting historic of symbols: {}".format(symbols_tickers))
        symbols_history = cls.__get_symbols_history(symbols_tickers=symbols_tickers, period=period,
                                                    actions=actions)

        symbols_data = list()
        for symbol in symbols_tickers:
            symbol_info = yf_ticker_info(symbol)
            name = symbol_info.info.get('shortName')
            if name is None:
                name = symbol_info.info.get('longName', 'Name_Unknown')
            name = name.split(',')[0]
            isin = symbol_info.isin
            symbols_history[symbol].columns = symbols_history[symbol].columns.droplevel(1)
            symbols_data.append(cls.symbol_information(ticker=symbol,
                                                       history=symbols_history[symbol],
                                                       name=name, isin=isin))
            time.sleep(1)
        return tuple(symbols_data)

    @staticmethod
    def __get_symbols_history(symbols_tickers, period: str = 'max',
                              actions: bool = False) -> dict[str, pandas.DataFrame]:
        # Divides symbols_tickers in chunks for avoid to overload yahoo finance api
        chunk_len = 1000 if len(symbols_tickers) > 1000 else len(symbols_tickers)
        chunks = [symbols_tickers[i:i+chunk_len] for i in range(0, len(symbols_tickers), chunk_len)]

        hist_data = dict().fromkeys(symbols_tickers)
        for chunk in chunks:
            chunk_data = yf_tickers(tickers=chunk).history(period=period, actions=actions)
            for symbol in chunk:
                hist_data[symbol] = chunk_data.filter(like=symbol, axis=1)

        return hist_data
