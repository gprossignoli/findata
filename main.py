from Ticker.domain import settings as st
from Ticker.application.obtain_tickers_use_case import ObtainTickersUseCase

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    ObtainTickersUseCase(exchanges=['^GSPC','^IBEX']).execute()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
