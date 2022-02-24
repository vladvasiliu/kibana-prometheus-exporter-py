from urllib.parse import urljoin

from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily


class TimestampMixin(object):
    """Add timestamps to *MetricFamily

    The goal is to be a generic drop-in replacement for *MetricFamily.
    That means that we can be called with the exact same signature as the original class.
    We don't care about any other argument.
    The sole assumption is that timestamp is not an argument expected by *MetricFamily.
    """

    def __init__(self, *args, **kwargs):
        try:
            self._timestamp = kwargs.pop("timestamp")
        except KeyError:
            self._timestamp = None
        super(TimestampMixin, self).__init__(*args, **kwargs)

    def add_metric(self, *args, **kwargs):
        if "timestamp" not in kwargs:
            kwargs["timestamp"] = self._timestamp
        super(TimestampMixin, self).add_metric(*args, **kwargs)


class TimestampGaugeMetricFamily(TimestampMixin, GaugeMetricFamily):
    pass


class TimestampCounterMetricFamily(TimestampMixin, CounterMetricFamily):
    pass


def url_join(host: str, path: str) -> str:
    """Produce an URL as expected when the host part has a path.

    The idea is to always have the host end with a `/` and the path be relative. This way `urljoin` keeps both.
    As `urljoin` removes superfluous slashes, there's no need to check wether `host` ends with one.

    This addresses https://github.com/vladvasiliu/kibana-prometheus-exporter-py/issues/4
    """
    host += "/"
    path = path.lstrip("/")
    return urljoin(host, path)
