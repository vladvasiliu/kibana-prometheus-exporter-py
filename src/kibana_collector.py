from datetime import datetime

from prometheus_client.core import CounterMetricFamily, InfoMetricFamily, StateSetMetricFamily, GaugeMetricFamily

from requests import get
from requests.compat import urljoin


def datestring_to_timestamp(date_str: str) -> float:
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()


def _status(status: dict) -> (StateSetMetricFamily, GaugeMetricFamily):
    status_dict = {state: state == status['overall']['state'] for state in ['red', 'yellow', 'green']}
    since = datestring_to_timestamp(status['overall']['since'])
    status = StateSetMetricFamily('kibana_status', 'Kibana Status', value=status_dict)
    since = GaugeMetricFamily('kibana_status_since', 'Last change of status, in seconds since epoch', value=since)
    return status, since


def _process(process_dict: dict) -> (GaugeMetricFamily,
                                     GaugeMetricFamily,
                                     GaugeMetricFamily,
                                     GaugeMetricFamily,
                                     CounterMetricFamily):
    heap_total = GaugeMetricFamily('kibana_process_memory_heap_total_bytes',
                                   'Total heap size in bytes',
                                   value=process_dict['memory']['heap']['total_in_bytes'])
    heap_used = GaugeMetricFamily('kibana_process_memory_heap_used_bytes',
                                  'Used heap size in bytes',
                                  value=process_dict['memory']['heap']['used_in_bytes'])
    size_limit = GaugeMetricFamily('kibana_process_memory_heap_size_limit_bytes',
                                   'Heap size limit in bytes',
                                   value=process_dict['memory']['heap']['size_limit'])
    resident_set_size = GaugeMetricFamily('kibana_process_memory_resident_set_size_bytes',
                                          'Memory resident set size',
                                          value=process_dict['memory']['resident_set_size_in_bytes'])
    uptime = CounterMetricFamily('kibana_process_uptime_seconds',
                                 'Kibana process uptime in seconds',
                                 value=process_dict['uptime_in_millis'] / 1000)

    return heap_used, heap_total, size_limit, resident_set_size, uptime


def _os_load(load_dict: dict) -> (GaugeMetricFamily, GaugeMetricFamily, GaugeMetricFamily):
    return (GaugeMetricFamily('kibana_os_load_%s' % key,
                              'Kibana OS load %s' % key,
                              value=value) for key, value in load_dict.items())


def _os_memory(mem_dict: dict) -> (GaugeMetricFamily, GaugeMetricFamily, GaugeMetricFamily):
    return (GaugeMetricFamily('kibana_os_memory_%s_bytes' % key,
                              'Kibana %s OS memory' % key,
                              value=value) for key, value in mem_dict.items())


def _os(os_dict: dict) -> iter:
    result = []
    result.extend(_os_load(os_dict['load']))
    result.extend(_os_memory(os_dict['memory']))
    result.append(CounterMetricFamily('kibana_os_uptime_seconds',
                                      'Kibana OS uptime in seconds',
                                      value=os_dict['uptime_in_millis'] / 1000))
    return result


def _requests(req_dict: dict) -> iter:
    total = CounterMetricFamily('kibana_requests_total',
                                'Total requests serviced',
                                value=req_dict['total'])
    disconnects = CounterMetricFamily('kibana_requests_disconnects',
                                      'Total requests disconnected',
                                      value=req_dict['disconnects'])
    per_status = CounterMetricFamily('kibana_requests',
                                     'Total requests by status code',
                                     labels=['status_code'])

    for code, count in req_dict['status_codes'].items():
        per_status.add_metric([code], count)

    return total, disconnects, per_status


def _response_times(rt_dict: dict) -> (GaugeMetricFamily, GaugeMetricFamily):
    max_rt = GaugeMetricFamily('kibana_response_time_max_seconds',
                               'Kibana maximum response time in seconds',
                               value=rt_dict['max_in_millis'] / 1000)
    avg_rt = GaugeMetricFamily('kibana_response_time_avg_seconds',
                               'Kibana average response time in seconds',
                               value=rt_dict['avg_in_millis'] / 1000)
    return max_rt, avg_rt


def _metrics(metrics_dict: dict):
    # last_updated = datestring_to_timestamp(metrics_dict['last_updated'])
    metrics = list(_process(metrics_dict['process']))
    metrics.extend(_os(metrics_dict['os']))
    metrics.extend(_requests(metrics_dict['requests']))
    metrics.extend(_response_times(metrics_dict['response_times']))
    return metrics


class KibanaCollector(object):
    def __init__(self, host: str, path: str = '/api/status'):
        self._url = urljoin(host, path)

    def _fetch_stats(self) -> dict:
        r = get(self._url)
        r.raise_for_status()
        return r.json()

    def collect(self):
        stats = self._fetch_stats()
        yield InfoMetricFamily('kibana_version', 'Kibana Version', value=stats['version'])
        yield from _status(stats['status'])
        yield from _metrics(stats['metrics'])
