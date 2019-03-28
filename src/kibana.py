from requests import get
from requests.compat import urljoin


class Kibana(object):
    def __init__(self, host: str, path: str='/api/status'):
        self._url = urljoin(host, path)

    def stats(self) -> dict:
        r = get(self._url)
        r.raise_for_status()
        return r.json()
