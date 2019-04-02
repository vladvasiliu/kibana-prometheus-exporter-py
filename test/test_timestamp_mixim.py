from unittest import TestCase

from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

from helpers import TimestampCounterMetricFamily, TimestampGaugeMetricFamily


class TimestampMixinTestBase(TestCase):
    def test_timestamp_metric_family_has_timestamp_if_set(self):
        timestamp = 214
        t = TimestampGaugeMetricFamily('some_name', 'some description', timestamp=timestamp)
        self.assertEquals(t._timestamp, timestamp)

    def test_timestamp_metric_family_has_none_timestamp_if_unset(self):
        t = TimestampGaugeMetricFamily('some_name', 'some description')
        self.assertIsNone(t._timestamp)

    def test_timestamp_metric_family_sets_timestamp_on_metrics_implicit_metrics(self):
        timestamp = 214
        t = TimestampGaugeMetricFamily('some_name', 'some description', timestamp=timestamp, value=2)
        self.assertEqual(t.samples[0].timestamp, timestamp)

    def test_timestamp_metric_family_sets_timestamp_on_metrics_add_metric(self):
        timestamp = 214
        t = TimestampGaugeMetricFamily('some_name', 'some description', timestamp=timestamp)
        t.add_metric(labels=[], value=123)
        self.assertEqual(t.samples[0].timestamp, timestamp)

    def test_timestamp_metric_family_keeps_timestamp_from_add_metric(self):
        timestamp = 214
        t = TimestampGaugeMetricFamily('some_name', 'some description', timestamp=timestamp)
        t.add_metric(labels=[], value=123, timestamp=234)
        self.assertEqual(t.samples[0].timestamp, 234)
