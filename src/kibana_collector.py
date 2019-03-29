from datetime import datetime
from itertools import chain

from prometheus_client.core import InfoMetricFamily, StateSetMetricFamily, GaugeMetricFamily

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
    def _status_metrics(status: dict) -> (StateSetMetricFamily, GaugeMetricFamily):
        status_dict = {state: state == status['overall']['state'] for state in ['red', 'yellow', 'green']}
        since = datetime.strptime(status['overall']['since'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()
        status = StateSetMetricFamily('kibana_status', 'Kibana Status', value=status_dict)
        since = GaugeMetricFamily('kibana_status_since', 'Last change of status, in seconds since epoch', value=since)
        return status, since

    def collect(self):
        stats = self._fetch_stats()
        yield InfoMetricFamily('kibana_version', 'Kibana Version', value=stats['version'])
        yield from self._status_metrics(stats['status'])
