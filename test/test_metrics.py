from unittest import TestCase

from kibana_prometheus_exporter.kibana_collector import Metrics


class TestMetrics(TestCase):
    def setUp(self) -> None:
        self.metrics_dict = {
            "last_updated": "2019-04-02T03:56:41.078Z",
            "collection_interval_in_millis": 15000,
            "process": {
                "memory": {
                    "heap": {"total_in_bytes": 175874048, "used_in_bytes": 157139288, "size_limit": 1526909922},
                    "resident_set_size_in_bytes": 285655040,
                },
                "event_loop_delay": 0.08109402656555176,
                "pid": 18595,
                "uptime_in_millis": 2494490,
            },
            "os": {
                "load": {"1m": 0.16357421875, "5m": 0.13720703125, "15m": 0.13037109375},
                "memory": {"total_in_bytes": 8257908736, "free_in_bytes": 193777664, "used_in_bytes": 8064131072},
                "uptime_in_millis": 1212738000,
                "platform": "linux",
                "platformRelease": "linux-4.15.0-1034-aws",
                "distro": "Ubuntu Linux",
                "distroRelease": "Ubuntu Linux-18.04",
                "cgroup": {
                    "cpuacct": {"control_group": "/system.slice/kibana.service", "usage_nanos": 24967412414},
                    "cpu": {
                        "control_group": "/system.slice/kibana.service",
                        "cfs_period_micros": 100000,
                        "cfs_quota_micros": -1,
                        "stat": {
                            "number_of_elapsed_periods": 0,
                            "number_of_times_throttled": 0,
                            "time_throttled_nanos": 0,
                        },
                    },
                },
            },
            "response_times": {"avg_in_millis": 2.3333333333333335, "max_in_millis": 3},
            "requests": {"disconnects": 0, "statusCodes": {}, "total": 3, "status_codes": {"302": 3}},
            "concurrent_connections": 0,
        }

    def test_all_metrics_have_timestamps(self):
        metrics = Metrics(self.metrics_dict)
        for metric in metrics:
            for sample in metric.samples:
                self.assertIsNotNone(sample.timestamp, sample)
