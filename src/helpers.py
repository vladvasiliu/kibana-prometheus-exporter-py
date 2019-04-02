from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily


class TimestampMixin(object):
    def __init__(self, *args, **kwargs):
        try:
            self._timestamp = kwargs.pop('timestamp')
        except KeyError:
            pass
        super(TimestampMixin, self).__init__(*args, **kwargs)


class TimestampGaugeMetricFamily(TimestampMixin, GaugeMetricFamily):
    pass


class TimestampCounterMetricFamily(TimestampMixin, CounterMetricFamily):
    pass
