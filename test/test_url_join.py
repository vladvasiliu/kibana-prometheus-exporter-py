from unittest import TestCase

from helpers import url_join


class TestURLJoin(TestCase):
    def test_bare_host_and_path_with_slash(self):
        host = "http://example.com"
        path = "/some/path"
        self.assertEqual(url_join(host, path), "http://example.com/some/path")

    def test_bare_host_and_path_without_slash(self):
        host = "http://example.com"
        path = "some/path"
        self.assertEqual(url_join(host, path), "http://example.com/some/path")

    def test_host_with_slash_and_path_with_slash(self):
        host = "http://example.com/"
        path = "/some/path"
        self.assertEqual(url_join(host, path), "http://example.com/some/path")

    def test_host_with_slash_and_path_without_slash(self):
        host = "http://example.com/"
        path = "some/path"
        self.assertEqual(url_join(host, path), "http://example.com/some/path")

    def test_host_with_path_no_slash_and_path_with_slash(self):
        host = "http://example.com/test"
        path = "/some/path"
        self.assertEqual(url_join(host, path), "http://example.com/test/some/path")

    def test_host_with_path_no_slash_and_path_without_slash(self):
        host = "http://example.com/test"
        path = "some/path"
        self.assertEqual(url_join(host, path), "http://example.com/test/some/path")

    def test_host_with_path_and_slash_and_path_without_slash(self):
        host = "http://example.com/test/"
        path = "some/path"
        self.assertEqual(url_join(host, path), "http://example.com/test/some/path")

    def test_host_with_path_and_slash_and_path_with_slash(self):
        host = "http://example.com/test/"
        path = "/some/path"
        self.assertEqual(url_join(host, path), "http://example.com/test/some/path")
