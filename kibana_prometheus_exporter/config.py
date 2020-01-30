import logging
import os

from requests.utils import get_netrc_auth

from _version import VERSION

DEFAULT_PORT = 9563

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.kibana_url = os.getenv('KIBANA_URL')
        listen_port = os.getenv('LISTEN_PORT', DEFAULT_PORT)
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.kibana_login = os.getenv('KIBANA_LOGIN')
        self.kibana_password = os.getenv('KIBANA_PASSWORD')
        self.version = VERSION

        try:
            self.listen_port = int(listen_port)
        except ValueError as e:
            logger.critical("Listen port must be an integer: %s", e)
            raise ValueError("Listen port must be an integer")

        numeric_level = getattr(logging, self.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            logger.critical('Invalid log level: %s' % numeric_level)
            raise ValueError('Invalid log level: %s. Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.')
        logging.basicConfig(level=numeric_level)

        if not self.kibana_url:
            logger.critical('The Kibana URL is required.')
            raise ValueError('The Kibana URL cannot be empty.')

    def description(self):
        config_list = [
            ('Listen port:', self.listen_port),
            ('Log level:', self.log_level),
            ('Kibana URL:', self.kibana_url),
        ]
        # check if netrc is available
        netrc_auth = get_netrc_auth(self.kibana_url)
        if netrc_auth:
            config_list.append(('Kibana login (from netrc):', netrc_auth[0]))
            config_list.append(('Kibana password (from netrc):', '***'))
        elif self.kibana_login:
            config_list.append(('Kibana login:', self.kibana_login))
            config_list.append(('Kibana password:', '***'))

        max_length = max(map(lambda x: len(x[0]), config_list))
        desc = '== CONFIGURATION ==\n'
        line_template = "%-" + str(max_length) + "s\t%s\n"
        for line in config_list:
            desc += (line_template % line)
        return desc
