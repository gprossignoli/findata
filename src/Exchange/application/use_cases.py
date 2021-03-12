from src.Exchange.domain.ports.use_case_interface import UseCaseInterface
from src.Exchange.application.scraper_adapter import ScraperAdapter
from src.Exchange.infraestructure.mongo_adapter import MongoAdapter


class ObtainExchangeTickersUseCase(UseCaseInterface):
    def execute(self, exchanges: tuple[str, ...] = ("^IBEX",)):
        """
        This use case fetches for tickers that compounds each stock exchange and then saves it
        into a mongo collection.

        :param exchanges: Stock exchange tickers from which we want to get the tickers.
        """

        ScraperAdapter(repository=MongoAdapter()).fetch_stocks(exchanges)
