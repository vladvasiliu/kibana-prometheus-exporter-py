from prometheus_client.core import InfoMetricFamily

from requests import get
from requests.compat import urljoin


class KibanaCollector(object):
    def __init__(self, host: str, path: str = '/api/status'):
        self._url = urljoin(host, path)

    def _fetch_stats(self) -> dict:
        r = get(self._url)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _version_metric(version: dict) -> InfoMetricFamily:
        return InfoMetricFamily('kibana_version', 'Kibana Version', value=version)

    def collect(self):
        stats = self._fetch_stats()
        yield self._version_metric(stats['version'])
