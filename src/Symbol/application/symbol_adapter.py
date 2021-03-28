import time

from pandas import DataFrame

from src.Symbol.domain.ports.symbol_service_interface import SymbolServiceInterface
from src.Symbol.domain.symbol import Symbol
from src import settings as st


class SymbolAdapter(SymbolServiceInterface):

    def fetch_all_symbols(self) -> tuple[Symbol, ...]:
        symbols = []

        exchanges = self.exchanges_repository.get_exchanges()
        for exchange in exchanges:
            if exchange.symbols:
                st.logger.info("Fetching symbols for exchange: {}".format(exchange.ticker))
                symbols_info = self.symbols_repository.fetch_symbols(exchange.symbols)
                for symbol_info in symbols_info:
                    if symbol_info.isin == '-' or symbol_info.name == 'Name_Unknown':
                        st.logger.info("Discarding symbol: {}".format(symbol_info.ticker))
                        continue
                    # holes gets filled with the previous data,
                    # and it discards all the indexes until the first valid index
                    historical_data = symbol_info.history.fillna(method='ffill').dropna()
                    symbols.append(self.__create_symbol_entity(ticker=symbol_info.ticker,
                                                               name=symbol_info.name,
                                                               isin=symbol_info.isin,
                                                               historical_data=historical_data))

                # 5 secs between executions to avoid overloading yahoo finance api
                break
                time.sleep(5)
        return tuple(symbols)

    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        self.publisher.publish_symbols(symbols)

    @staticmethod
    def __create_symbol_entity(ticker: str, historical_data: DataFrame, name: str = None, isin: str = None):
        return Symbol(ticker=ticker, name=name, isin=isin, historical_data=historical_data)