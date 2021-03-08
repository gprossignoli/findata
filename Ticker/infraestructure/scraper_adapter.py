import re
import requests

from bs4 import BeautifulSoup
import ujson


class ScraperAdapter:
    @staticmethod
    def obtain_tickers(exchange: str) -> tuple[str]:
        """
        Scraps the response, looking for the list of tickers
        :param exchange: Ticker of the stock exchange.
        :return: Tickers which compound the exchange.
        """
        req = requests.get(url=f'https://es.finance.yahoo.com/quote/{exchange}/components')
        soup = BeautifulSoup(req.content)
        script = soup.find("script", text=re.compile("root.App.main"))
        # It's necessary to use json, because the page uses react for loading the data.
        data = ujson.loads(re.search("root.App.main\s+=\s+(\{.*\})", str(script)).group(1))
        tickers = data['context']['dispatcher']['stores']['QuoteSummaryStore']['components']['components']
        return tuple(tickers) if tickers is not None else tuple()
