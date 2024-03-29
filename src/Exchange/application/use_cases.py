from apscheduler.schedulers.background import BackgroundScheduler

from src.Exchange.domain.ports.use_case_interface import UseCaseInterface
from src.Exchange.application.scraper_adapter import ScraperAdapter
from src.Exchange.infraestructure.mongo_adapter import MongoAdapter
from src import settings as st


class ObtainExchangeTickersUseCase(UseCaseInterface):
    def execute(self):
        """
        This use case fetches for tickers that compounds each stock exchange and then saves it
        into a mongo collection.
        """

        ScraperAdapter(repository=MongoAdapter()).fetch_stocks(exchange_tickers=st.exchanges)

    @staticmethod
    def execute_with_scheduler(scheduler: BackgroundScheduler):
        scheduler.add_job(ScraperAdapter(repository=MongoAdapter()).fetch_stocks,
                          'cron', day_of_week='sat',
                          hour=3, minute=30, kwargs={"exchange_tickers": st.exchanges},
                          misfire_grace_time=None)

