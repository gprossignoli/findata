from apscheduler.schedulers.background import BackgroundScheduler

from src.Exchange.domain.ports.use_case_interface import UseCaseInterface
from src.Exchange.infraestructure.mongo_adapter import MongoAdapter as MongoExchangesAdapter
from src.Symbol.application.yfinance_adapter import YFinanceAdapter
from src.Symbol.infraestructure.rabbitmq_publisher_adapter import RabbitmqPublisherAdapter
from src import settings as st


class FetchSymbolsData(UseCaseInterface):
    def execute(self):
        """
        This use case fetches for tickers that compounds each stock exchange and then saves it
        into a mongo collection.
        """
        st.logger.info("Executing fetch symbols use case.")
        symbols_domain_service = YFinanceAdapter(symbols_repository=None,
                                                 exchanges_repository=MongoExchangesAdapter(),
                                                 publisher=RabbitmqPublisherAdapter())
        symbols = symbols_domain_service.fetch_all_symbols()
        symbols_domain_service.publish_symbols(symbols)
        st.logger.info("Fetch symbols use case finished.")

    @staticmethod
    def execute_with_scheduler(scheduler: BackgroundScheduler):
        scheduler.add_job(YFinanceAdapter(symbols_repository=None,
                                          exchanges_repository=MongoExchangesAdapter(),
                                          publisher=RabbitmqPublisherAdapter())
                          .fetch_all_symbols,
                          'cron', day_of_week='mon',
                          hour=4, minute=30,
                          misfire_grace_time=None)
        scheduler.start()
