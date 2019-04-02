from datetime import datetime
import logging
from typing import Iterator

from prometheus_client.core import InfoMetricFamily, StateSetMetricFamily, GaugeMetricFamily, Metric

from requests import get
from requests.compat import urljoin
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException

from helpers import TimestampGaugeMetricFamily, TimestampCounterMetricFamily


logger = logging.getLogger(__name__)


def datestring_to_timestamp(date_str: str) -> float:
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()


def _info(info: dict) -> InfoMetricFamily:
    info = {k: str(v) for k, v in info.items()}
    return InfoMetricFamily('kibana_version', 'Kibana Version', value=info)


def _status(status: dict) -> (StateSetMetricFamily, GaugeMetricFamily):
    status_dict = {state: state == status['overall']['state'] for state in ['red', 'yellow', 'green']}
    since = datestring_to_timestamp(status['overall']['since'])
    status = StateSetMetricFamily('kibana_status', 'Kibana Status', value=status_dict)
    since = GaugeMetricFamily('kibana_status_since', 'Last change of status, in seconds since epoch', value=since)
    return status, since


class Metrics(object):
    def __init__(self, metrics_dict: dict):
        self._timestamp = datestring_to_timestamp(metrics_dict['last_updated'])
        self._metrics_dict = metrics_dict

    def __iter__(self):
        yield from self._response_times()
        yield from self._requests()
        yield from self._process()
        yield from self._os()

    def _os(self) -> Iterator[Metric]:
        os_dict = self._metrics_dict['os']

        yield from (TimestampGaugeMetricFamily('kibana_os_load_%s' % key,
                                               'Kibana OS load %s' % key,
                                               value=value,
                                               timestamp=self._timestamp) for key, value in os_dict['load'].items())

        yield from (TimestampGaugeMetricFamily('kibana_os_memory_%s_bytes' % key.split('_')[0],
                                               'Kibana %s OS memory' % key.split('_')[0],
                                               value=value,
                                               timestamp=self._timestamp) for key, value in os_dict['memory'].items())

        yield TimestampCounterMetricFamily('kibana_os_uptime_seconds',
                                           'Kibana OS uptime in seconds',
                                           value=os_dict['uptime_in_millis'] / 1000,
                                           timestamp=self._timestamp)

    def _response_times(self) -> Iterator[Metric]:
        rt_dict = self._metrics_dict['response_times']

        yield TimestampGaugeMetricFamily('kibana_response_time_max_seconds',
                                         'Kibana maximum response time in seconds',
                                         value=rt_dict['max_in_millis'] / 1000,
                                         timestamp=self._timestamp)

        # Kibana statistics lib can sometimes return NaN for this value.
        # If that is the case, this is set to 0 in order to avoid gaps in the time series.
        # Reference: https://github.com/elastic/kibana/blob/6.7/src/server/status/lib/metrics.js#L73
        # NaN is converted to `undefined` which then has the whole field removed from the response JSON
        yield TimestampGaugeMetricFamily('kibana_response_time_avg_seconds',
                                         'Kibana average response time in seconds',
                                         value=rt_dict.setdefault('avg_in_millis', 0) / 1000,
                                         timestamp=self._timestamp)

    def _requests(self) -> Iterator[Metric]:
        req_dict = self._metrics_dict['requests']
        yield TimestampGaugeMetricFamily('kibana_requests_total',
                                         'Total requests serviced',
                                         value=req_dict['total'],
                                         timestamp=self._timestamp)

        yield TimestampGaugeMetricFamily('kibana_requests_disconnects',
                                         'Total requests disconnected',
                                         value=req_dict['disconnects'],
                                         timestamp=self._timestamp)

        per_status = TimestampGaugeMetricFamily('kibana_requests',
                                                'Total requests by status code',
                                                labels=['status_code'],
                                                timestamp=self._timestamp)

        for code, count in req_dict['status_codes'].items():
            per_status.add_metric(labels=[code], value=count)

        yield per_status

    def _process(self) -> Iterator[Metric]:
        process_dict = self._metrics_dict['process']

        yield TimestampGaugeMetricFamily('kibana_process_memory_heap_total_bytes',
                                         'Total heap size in bytes',
                                         value=process_dict['memory']['heap']['total_in_bytes'],
                                         timestamp=self._timestamp)
        yield TimestampGaugeMetricFamily('kibana_process_memory_heap_used_bytes',
                                         'Used heap size in bytes',
                                         value=process_dict['memory']['heap']['used_in_bytes'],
                                         timestamp=self._timestamp)

        yield TimestampGaugeMetricFamily('kibana_process_memory_heap_size_limit_bytes',
                                         'Heap size limit in bytes',
                                         value=process_dict['memory']['heap']['size_limit'],
                                         timestamp=self._timestamp)

        yield TimestampGaugeMetricFamily('kibana_process_memory_resident_set_size_bytes',
                                         'Memory resident set size',
                                         value=process_dict['memory']['resident_set_size_in_bytes'],
                                         timestamp=self._timestamp)

        yield TimestampCounterMetricFamily('kibana_process_uptime_seconds',
                                           'Kibana process uptime in seconds',
                                           value=process_dict['uptime_in_millis'] / 1000,
                                           timestamp=self._timestamp)


class KibanaCollector(object):
    def __init__(self, host: str, path: str = '/api/status', kibana_login: str = None, kibana_password: str = None):
        self._url = urljoin(host, path)
        self._kibana_login = kibana_login
        self._kibana_password = kibana_password

    def _fetch_stats(self) -> dict:
        if self._kibana_login:
            auth = (self._kibana_login, self._kibana_password)
        else:
            auth = None
        r = get(self._url, auth=auth)
        r.raise_for_status()
        return r.json()

    def collect(self):
        kibana_up = GaugeMetricFamily('kibana_node_reachable', 'Kibana node was reached', value=0)
        try:
            stats = self._fetch_stats()
        except ConnectionError as e:
            logger.warning('Got a connection error while trying to contact Kibana:\n%s' % e)
        except Timeout as e:
            logger.warning('Got a timeout while trying to contact Kibana:\n%s' % e)
        except HTTPError as e:
            logger.warning('Got a HTTP error %s while trying to contact Kibana:\n%s' % (e.response.status_code, e))
        except RequestException as e:
            logger.warning('Got a RequestException while trying to contact Kibana:\n%s' % e)
        else:
            kibana_up = GaugeMetricFamily('kibana_node_reachable', 'Kibana node was reached', value=1)
            yield _info(stats['version'])
            yield from _status(stats['status'])
            yield from Metrics(stats['metrics'])
        finally:
            yield kibana_up
