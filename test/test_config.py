from unittest import TestCase

from hypothesis import given, strategies as st

import config


def _everything_except(excluded_types):
    return st.from_type(type).flatmap(st.from_type).filter(lambda x: not isinstance(x, excluded_types))


class TestCheckURL(TestCase):
    def test_full_url_with_params(self):
        url = "http://example.com/some/path?x=2"
        self.assertEqual(config._check_url(url), url)

    def test_full_url_without_params(self):
        url = "http://example.com/some/path"
        self.assertEqual(config._check_url(url), url)

    def test_url_without_path(self):
        for url in ["http://example.com/", "http://example.com"]:
            with self.subTest(url=url):
                self.assertEqual(config._check_url(url), url)

    def test_raises_with_missing_scheme(self):
        url = "example.com"
        self.assertRaises(ValueError, config._check_url, url)

    def test_raises_for_empty_scheme(self):
        url = "://example.com"
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
