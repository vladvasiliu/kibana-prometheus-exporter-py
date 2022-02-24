import logging
from unittest import TestCase

from hypothesis import example, given, strategies as st, assume
from hypothesis.provisional import domains, urls

from kibana_prometheus_exporter import config


def _everything_except(excluded_types):
    return st.from_type(type).flatmap(st.from_type).filter(lambda x: not isinstance(x, excluded_types))


def _everything_except_int_like():
    def _not_convertible_to_int(val):
        try:
            int_val = int(str(val))
        except Exception:
            return True
        else:
            return str(int_val) != str(val)

    return _everything_except(int).filter(_not_convertible_to_int)


MIN_PORT = 0
MAX_PORT = 2**16 - 1
PORTS_VALID = st.integers(min_value=MIN_PORT, max_value=MAX_PORT)
PORTS_INVALID = st.integers().filter(lambda x: x < MIN_PORT or x > MAX_PORT)


@st.composite
def _urls_with_out_of_bounds_port(draw):
    domain = draw(domains())
    port = draw(PORTS_INVALID)
    return "http://%s:%d" % (domain, port)


@st.composite
def _urls_with_bogus_port(draw):
    domain = draw(domains())
    port = draw(_everything_except_int_like)
    return "http://%s:%s" % (domain, port)


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

    @given(_urls_with_out_of_bounds_port())
    def test_raises_for_out_of_bounds_port_number(self, url):
        self.assertRaises(ValueError, config._check_url, url)

    @given(domain=domains(), port=_everything_except_int_like())
    def test_raises_for_bogus_port_number(self, domain, port):
        assume(str(port) not in ("[]", ""))  # urllib bug: https://bugs.python.org/issue36338
        assume(str(port) not in ("/"))  # An empty port is allowed
        url = "http://%s:%s" % (domain, port)
        self.assertRaises(ValueError, config._check_url, url)


class TestCheckPort(TestCase):
    @given(PORTS_VALID)
    def test_port_range_works(self, port):
        self.assertEqual(config._check_port(port), port)

    @given(PORTS_INVALID)
    def test_outside_port_range_fails(self, port):
        self.assertRaises(ValueError, config._check_port, port)

    @given(port=_everything_except_int_like())
    def test_raises_for_text(self, port):
        assume(not str(port).isnumeric())
        self.assertRaises(ValueError, config._check_port, port)


class TestCheckLogLevel(TestCase):
    def test_check_log_level_works_for_expected_values(self):
        for level in config.LOG_LEVELS:
            with self.subTest(level):
                self.assertEqual(config._check_log_level(level), getattr(logging, level.upper()))

    @given(st.text().filter(lambda x: x.upper() not in config.LOG_LEVELS))
    def test_check_log_level_raises_for_random_text(self, value):
        self.assertRaises(ValueError, config._check_log_level, value)

    @given(_everything_except(str))
    def test_check_log_level_raises_for_random_non_text_stuff(self, value):
        self.assertRaises(ValueError, config._check_log_level, value)
