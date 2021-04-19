from dataclasses import dataclass

from pandas import DataFrame


@dataclass
class Symbol:
    ticker: str
    isin: str
    name: str
    historical_data: DataFrame


@dataclass
class Stock(Symbol):
    exchange: str


@dataclass
class SymbolInformation:
    ticker: str
    isin: str
    name: str
    exchange: str


@dataclass
class IndexInformation:
    ticker: str
    isin: str
    name: str
