from src.Exchange.application.use_cases import ObtainExchangeTickersUseCase


if __name__ == '__main__':
    ObtainExchangeTickersUseCase().execute_with_scheduler()
    while True:
        pass

