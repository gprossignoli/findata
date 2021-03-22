import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3 import Retry

from src import settings as st


class HttpRequestException(Exception):
    pass


class HttpRequest:
    def __init__(self, status_forcelist: list[int]):
        self.session = requests.session()
        # backoff_factor time expected = [5, 10, 20, 40, 80] segs.
        retries_conf = Retry(total=5, connect=1, read=3, redirect=2, status=5, other=1,
                             backoff_factor=5, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retries_conf)
        self.session.mount(prefix='https://', adapter=adapter)
        self.session.mount(prefix='http://', adapter=adapter)

    def get(self, url: str, timeout=None) -> requests.Response:
        try:
            if timeout is not None:
                return self.session.get(url=url, timeout=timeout)
            return self.session.get(url=url)
        except RequestException as e:
            st.logger.exception(e)
            raise
