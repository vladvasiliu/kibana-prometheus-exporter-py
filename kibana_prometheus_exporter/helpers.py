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
            self._timestamp = kwargs.pop('timestamp')
        except KeyError:
            self._timestamp = None
        super(TimestampMixin, self).__init__(*args, **kwargs)

    def add_metric(self, *args, **kwargs):
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = self._timestamp
        super(TimestampMixin, self).add_metric(*args, **kwargs)


class TimestampGaugeMetricFamily(TimestampMixin, GaugeMetricFamily):
    pass


class TimestampCounterMetricFamily(TimestampMixin, CounterMetricFamily):
    pass
