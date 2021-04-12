# findata
Application for financial data adquisition as part of my bachelor's final thesis.
It uses a fork of yfinance library, in which I made a few little fixes to be able to collect symbols with different formats other than US symbols.

In v1.0.0 the application has three use cases.
- ObtainTickersUseCase: This use case fetches for tickers that compounds each stock exchange and then saves it into a mongo collection. It runs weekly, every saturday at 03:30 a.m 
- FetchSymbolsData: This use case fetches for information and financial data of symbols that compounds the exchanges fetched previosly. It runs weekly every monday at 04:30 a.m
- FetchSymbolsInfo: This use case looks up the information, such as isin, name, etc, of symbols that compounds the exchanges fetched previosly and then sends this information through a message broker. It runs weekly every sunday at 03:30 a.m
