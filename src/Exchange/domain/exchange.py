from dataclasses import dataclass


@dataclass(init=True)
class Exchange:
    ticker: str
    symbols: tuple[str, ...]
