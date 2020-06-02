import logging
import os
from urllib.parse import urlsplit

from requests.utils import get_netrc_auth

from ._version import VERSION

DEFAULT_PORT = 9563

LOG_LEVELS = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL", "FATAL"]


class Config:
    def __init__(self):
        kibana_url = os.getenv("KIBANA_URL")
        listen_port = os.getenv("LISTEN_PORT", DEFAULT_PORT)
        log_level = os.getenv("LOG_LEVEL", "INFO")
        kibana_login = os.getenv("KIBANA_LOGIN")
        kibana_password = os.getenv("KIBANA_PASSWORD")
        ignore_ssl = os.getenv("IGNORE_SSL", "FALSE")
        requests_ca_bundle = os.getenv("REQUESTS_CA_BUNDLE", None)

        self.version = VERSION
        self.log_level = _check_log_level(log_level)
        logging.basicConfig(level=self.log_level)
        self.kibana_url = _check_url(kibana_url)
        self.listen_port = _check_port(listen_port)
        self.kibana_login = kibana_login
        self.kibana_password = kibana_password
        self.ignore_ssl = _check_ssl(ignore_ssl)
        self.requests_ca_bundle = _check_bundle(requests_ca_bundle)

        if not self.kibana_url:
            raise ValueError("The Kibana URL cannot be empty.")

    def description(self):
        config_list = [
            ("Listen port:", self.listen_port),
            ("Log level:", logging.getLevelName(self.log_level)),
            ("Kibana URL:", self.kibana_url),
        ]
        # check if netrc is available
        netrc_auth = get_netrc_auth(self.kibana_url)
        if netrc_auth:
            config_list.append(("Kibana login (from netrc):", netrc_auth[0]))
            config_list.append(("Kibana password (from netrc):", "***"))
        elif self.kibana_login:
            config_list.append(("Kibana login:", self.kibana_login))
            config_list.append(("Kibana password:", "***"))

        if self.ignore_ssl:
            config_list.append(("SSL verification:", "disabled"))
        else:
            config_list.append(("SSL verification:", "enabled"))

        if self.requests_ca_bundle:
            config_list.append(("Requests CA bundle path:", self.requests_ca_bundle))

        max_length = max(map(lambda x: len(x[0]), config_list))
        desc = "== CONFIGURATION ==\n"
        line_template = "%-" + str(max_length) + "s\t%s\n"
        for line in config_list:
            desc += line_template % line
        return desc


def _check_bundle(requests_ca_bundle: str) -> str:
    if requests_ca_bundle and not os.path.isfile(requests_ca_bundle):
        raise ValueError("REQUESTS_CA_BUNDLE should point to existing certficate")
    return requests_ca_bundle


def _check_url(url: str) -> str:
    split_url = urlsplit(url)
    if not all(split_url[:2]):
        raise ValueError("URL is malformed.")
    try:
        split_url.port
    except ValueError as e:
        raise ValueError("URL is malformed: %s" % e)
    return url


def _check_ssl(ignore_ssl: str) -> bool:
    if ignore_ssl.upper() == "TRUE":
        return True
    elif ignore_ssl.upper() == "FALSE":
        return False
    else:
        raise ValueError("IGNORE_SSL should be `True` or `False`")


def _check_port(port: str) -> int:
    if type(port) not in (str, int):
        raise ValueError("Listen port must be an integer. Got: %s" % (port,))
    try:
        # Avoid converting types that can be represented as an int but are not int-like, such as IPs
        port = int(port)
    except (OverflowError, TypeError, ValueError) as e:
        raise ValueError("Listen port must be an integer: %s" % e)
    if 0 <= port <= 65535:
        return port
    else:
        raise ValueError("Listen port must be between 1 and 65535")


def _check_log_level(log_level: str) -> int:
    try:
        return getattr(logging, log_level.upper())
    except (AttributeError, TypeError):
        raise ValueError("Invalid log level: %s. Must be one of %s." % (", ".join(LOG_LEVELS), log_level))
