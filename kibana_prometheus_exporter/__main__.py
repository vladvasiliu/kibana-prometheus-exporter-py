import asyncio
import logging
import sys

from prometheus_client.core import REGISTRY
from prometheus_client.exposition import start_http_server

from config import Config
from kibana_collector import KibanaCollector

logger = logging.getLogger(__name__)

try:
    config = Config()
except ValueError:
    logger.critical('Invalid configuration. Exiting.')
    sys.exit(1)


logger.info('Starting Kibana Prometheus exporter version %s\n' % config.version + config.description())

REGISTRY.register(KibanaCollector(config.kibana_url,
                                  kibana_login=config.kibana_login,
                                  kibana_password=config.kibana_password))

start_http_server(config.listen_port)

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.stop()
    loop.close()
