from Ticker.application.ticker_repository import TickerRepository


class ObtainTickersUseCase:
    def __init__(self, exchanges: tuple[str] = ("^IBEX",)):
        """
        This use case fetches for tickers that compounds each stock exchange.

        :param exchanges: Stock exchange from which we want to get the tickers.
        """

        self.exchanges = exchanges
        self.__ticker_repository = TickerRepository()

    def execute(self):
        for exchange in self.exchanges:
            tickers = self.__ticker_repository.obtain_all_tickers(exchange)
            try:
                self.__ticker_repository.store_tickers(exchange, tickers)
            except Exception as e:
                pass
