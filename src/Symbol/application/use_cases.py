from apscheduler.schedulers.background import BackgroundScheduler

from src.Exchange.domain.ports.use_case_interface import UseCaseInterface
from src.Exchange.infraestructure.mongo_adapter import MongoAdapter as MongoExchangesAdapter
from src.Symbol.application.yfinance_adapter import YFinanceAdapter
from src.Symbol.infraestructure.mongo_adapter import MongoAdapter as MongoSymbolsAdapter
from src.Symbol.infraestructure.rabbitmq_publisher_adapter import RabbitmqPublisherAdapter
from src import settings as st


class FetchSymbolsData(UseCaseInterface):
    def execute(self):
        """
        This use case fetches for information and financial data of symbols that compounds
        the exchanges fetched previosly.
        """
        st.logger.info("Executing fetch symbols use case.")
        symbols_domain_service = YFinanceAdapter(symbols_repository=MongoSymbolsAdapter(),
                                                 exchanges_repository=MongoExchangesAdapter(),
                                                 publisher=RabbitmqPublisherAdapter())
        symbols = symbols_domain_service.fetch_all_symbols()
        symbols_domain_service.publish_symbols(symbols)
        st.logger.info("Fetch symbols use case finished.")

    @staticmethod
    def execute_with_scheduler(scheduler: BackgroundScheduler):
        scheduler.add_job(YFinanceAdapter(symbols_repository=MongoSymbolsAdapter(),
                                          exchanges_repository=MongoExchangesAdapter(),
                                          publisher=RabbitmqPublisherAdapter())
                          .fetch_all_symbols,
                          'cron', day_of_week='mon',
                          hour=4, minute=30,
                          misfire_grace_time=None)


class FetchIndexesData(UseCaseInterface):
    def execute(self):
        """
        This use case fetches for information and financial data of the market indexes.
        """
        st.logger.info("Executing fetch symbols use case.")
        symbols_service = YFinanceAdapter(symbols_repository=MongoSymbolsAdapter(),
                                          exchanges_repository=MongoExchangesAdapter(),
                                          publisher=RabbitmqPublisherAdapter())
        indexes = symbols_service.fetch_indexes()
        symbols_service.publish_indexes(indexes)
        st.logger.info("Fetch symbols use case finished.")

    @staticmethod
    def execute_with_scheduler(scheduler: BackgroundScheduler):
        scheduler.add_job(YFinanceAdapter(symbols_repository=MongoSymbolsAdapter(),
                                          exchanges_repository=MongoExchangesAdapter(),
                                          publisher=RabbitmqPublisherAdapter())
                          .fetch_indexes,
                          'cron', day_of_week='mon',
                          hour=3, minute=30,
                          misfire_grace_time=None)


class FetchSymbolsInfo(UseCaseInterface):
    def execute(self):
        """
        This use case looks up the information, such as isin, name, etc, of symbols that compounds
        the exchanges fetched previosly.
        """
        st.logger.info("Executing fetch symbols info use case.")
        symbols_domain_service = YFinanceAdapter(symbols_repository=MongoSymbolsAdapter(),
                                                 exchanges_repository=MongoExchangesAdapter())
        symbols_domain_service.fetch_all_symbols_info()
        st.logger.info("Fetch symbols info use case finished.")

    @staticmethod
    def execute_with_scheduler(scheduler: BackgroundScheduler):
        scheduler.add_job(YFinanceAdapter(symbols_repository=MongoSymbolsAdapter(),
                                          exchanges_repository=MongoExchangesAdapter())
                          .fetch_all_symbols_info,
                          'cron', day_of_week='sun',
                          hour=3, minute=30,
                          misfire_grace_time=None)

