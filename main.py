import time

from apscheduler.schedulers.background import BackgroundScheduler

from src.Exchange.application.use_cases import ObtainExchangeTickersUseCase
from src.Symbol.application.use_cases import FetchSymbolsData, FetchIndexesData, FetchSymbolsInfo
from src import settings as st

if __name__ == '__main__':
    scheduler = BackgroundScheduler(logger=st.logger)

    ObtainExchangeTickersUseCase().execute_with_scheduler(scheduler)
    FetchSymbolsInfo().execute_with_scheduler(scheduler)
    FetchIndexesData().execute_with_scheduler(scheduler)
    FetchSymbolsData().execute_with_scheduler(scheduler)

    scheduler.start()
    while True:
        time.sleep(60)
        pass
