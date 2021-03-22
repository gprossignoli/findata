import time

from pandas import DataFrame

from src.Symbol.domain.symbol_service_interface import SymbolServiceInterface
from src.Symbol.domain.ticker import Symbol


class SymbolAdapter(SymbolServiceInterface):

    def fetch_all_symbols(self) -> tuple[Symbol, ...]:
        symbols = []

        exchanges = self.exchanges_repository.get_exchanges()
        for exchange in exchanges:
            if exchange.symbols:
                symbols_info = self.symbols_repository.fetch_symbols(exchange.symbols)
                for symbol_info in symbols_info:
                    # se rellenan los huecos con el precio anterior y
                    # se coge solo desde el dia que todos los valores son validos
                    historical_data = symbol_info.history.fillna(method='ffill').dropna(axis=0)

                    symbols.append(self.__create_symbol_entity(ticker=symbol_info.ticker,
                                                               historical_data=historical_data))
                # 30 secs between executions to avoid overloading yahoo finance api
                time.sleep(30)
        return tuple(symbols)

    def publish_symbols(self, symbols: tuple[Symbol, ...]) -> None:
        pass

    @staticmethod
    def __create_symbol_entity(ticker: str, historical_data: DataFrame, name: str = None, isin: str = None):
        return Symbol(ticker=ticker, name=None, isin=None, historical_data=historical_data)