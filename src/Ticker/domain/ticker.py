from dataclasses import dataclass
from collections import namedtuple

from pandas import DataFrame


tickers_to_load = namedtuple("tickers_to_load", ())

@dataclass
class Ticker:
    isin: str
    name: str
    historical_data: DataFrame
