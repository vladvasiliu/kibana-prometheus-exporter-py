import logging
from unittest import TestCase

from hypothesis import example, given, strategies as st
from hypothesis.provisional import domains, urls

import config


def _everything_except(excluded_types):
    return st.from_type(type).flatmap(st.from_type).filter(lambda x: not isinstance(x, excluded_types))


class TestCheckURL(TestCase):
    @given(urls())
    @example("http://example.com/some/path?x=2")
    @example("http://example.com/some/path")
    @example("http://example.com/")
    @example("http://example.com")
    def test_full_url_is_ok(self, url):
        self.assertEqual(config._check_url(url), url)

    @given(domains())
    @example(None)
    @example("example.com")
    @example("://example.com")
    def test_raises_for_missing_or_wrong_scheme(self, url):
        self.assertRaises(ValueError, config._check_url, url)


class TestCheckPort(TestCase):
    @given(st.integers(min_value=1, max_value=65535))
    def test_port_range_works(self, port):
        self.assertEqual(config._check_port(port), port)

    @given(st.integers().filter(lambda x: x < 1 or x > 65535))
    def test_outside_port_range_fails(self, port):
        self.assertRaises(ValueError, config._check_port, port)

    @given(port=_everything_except(int))
    def test_raises_for_text(self, port):
        self.assertRaises(ValueError, config._check_port, port)


log_levels = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "FATAL"]


class TestCheckLogLevel(TestCase):
    @given(st.text().filter(lambda x: x.upper() not in log_levels))
    def test_check_log_level_raises_for_random_text(self, value):
        self.assertRaises(ValueError, config._check_log_level, value)

    @given(_everything_except(str))
    def test_check_log_level_raises_for_random_non_text_stuff(self, value):
        self.assertRaises(ValueError, config._check_log_level, value)
