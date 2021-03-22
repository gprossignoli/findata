from dataclasses import dataclass


@dataclass(init=True)
class Exchange:
    ticker: str
    symbols: tuple[str, ...]

    def __repr__(self):
        return f'Ticker: {self.ticker}\nSymbols: {self.symbols}'
