from datetime import datetime
import logging

from prometheus_client.core import CounterMetricFamily, InfoMetricFamily, StateSetMetricFamily, GaugeMetricFamily

from requests import get
from requests.compat import urljoin
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException


logger = logging.getLogger(__name__)


def datestring_to_timestamp(date_str: str) -> float:
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()


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

    def _os(self):
        os_dict = self._metrics_dict['os']

        yield from (GaugeMetricFamily('kibana_os_load_%s' % key,
                                      'Kibana OS load %s' % key,
                                      value=value) for key, value in os_dict['load'].items())

        yield from (GaugeMetricFamily('kibana_os_memory_%s_bytes' % key.split('_')[0],
                                      'Kibana %s OS memory' % key.split('_')[0],
                                      value=value) for key, value in os_dict['memory'].items())

        yield CounterMetricFamily('kibana_os_uptime_seconds',
                                  'Kibana OS uptime in seconds',
                                  value=os_dict['uptime_in_millis'] / 1000)

    def _response_times(self) -> (GaugeMetricFamily, GaugeMetricFamily):
        rt_dict = self._metrics_dict['response_times']

        max_rt = GaugeMetricFamily('kibana_response_time_max_seconds',
                                   'Kibana maximum response time in seconds')
        max_rt.add_metric(labels=[], value=rt_dict['max_in_millis'] / 1000, timestamp=self._timestamp)

        # Kibana statistics lib can sometimes return NaN for this value.
        # If that is the case, this is set to 0 in order to avoid gaps in the time series.
        # Reference: https://github.com/elastic/kibana/blob/6.7/src/server/status/lib/metrics.js#L73
        # NaN is converted to `undefined` which then has the whole field removed from the response JSON
        avg_rt = GaugeMetricFamily('kibana_response_time_avg_seconds',
                                   'Kibana average response time in seconds')
        avg_rt.add_metric(labels=[], value=rt_dict.setdefault('avg_in_millis', 0) / 1000, timestamp=self._timestamp)
        return max_rt, avg_rt

    def _requests(self) -> iter:
        req_dict = self._metrics_dict['requests']
        total = GaugeMetricFamily('kibana_requests_total',
                                  'Total requests serviced')
        total.add_metric(labels=[], value=req_dict['total'], timestamp=self._timestamp)

        disconnects = GaugeMetricFamily('kibana_requests_disconnects',
                                        'Total requests disconnected')
        disconnects.add_metric(labels=[], value=req_dict['disconnects'], timestamp=self._timestamp)

        per_status = GaugeMetricFamily('kibana_requests',
                                       'Total requests by status code',
                                       labels=['status_code'])

        for code, count in req_dict['status_codes'].items():
            per_status.add_metric(labels=[code], value=count, timestamp=self._timestamp)

        return total, disconnects, per_status

    def _process(self) -> (GaugeMetricFamily, GaugeMetricFamily, GaugeMetricFamily, GaugeMetricFamily, CounterMetricFamily):
        process_dict = self._metrics_dict['process']

        heap_total = GaugeMetricFamily('kibana_process_memory_heap_total_bytes',
                                       'Total heap size in bytes')
        heap_total.add_metric(labels=[], value=process_dict['memory']['heap']['total_in_bytes'],
                              timestamp=self._timestamp)

        heap_used = GaugeMetricFamily('kibana_process_memory_heap_used_bytes',
                                      'Used heap size in bytes')
        heap_used.add_metric(labels=[], value=process_dict['memory']['heap']['used_in_bytes'],
                             timestamp=self._timestamp)

        size_limit = GaugeMetricFamily('kibana_process_memory_heap_size_limit_bytes',
                                       'Heap size limit in bytes')
        size_limit.add_metric(labels=[], value=process_dict['memory']['heap']['size_limit'],
                              timestamp=self._timestamp)

        resident_set_size = GaugeMetricFamily('kibana_process_memory_resident_set_size_bytes',
                                              'Memory resident set size')
        resident_set_size.add_metric(labels=[], value=process_dict['memory']['resident_set_size_in_bytes'],
                                     timestamp=self._timestamp)

        uptime = CounterMetricFamily('kibana_process_uptime_seconds',
                                     'Kibana process uptime in seconds')
        uptime.add_metric(labels=[], value=process_dict['uptime_in_millis'] / 1000,
                          timestamp=self._timestamp)

        return heap_used, heap_total, size_limit, resident_set_size, uptime


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
            # yield InfoMetricFamily('kibana_version', 'Kibana Version', value=stats['version'])
            # yield from _status(stats['status'])
            yield from Metrics(stats['metrics'])
        finally:
            yield kibana_up
