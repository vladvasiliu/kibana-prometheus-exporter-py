#!env python

import logging
import sys

from prometheus_client.twisted import MetricsResource
from prometheus_client.core import REGISTRY
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from config import Config
from kibana_collector import KibanaCollector

logger = logging.getLogger(__name__)

try:
    config = Config()
except ValueError:
    logger.critical('Invalid configuration. Exiting.')
    sys.exit(1)


logger.info('Starting Kibana Prometheus exporter v%s\n' % config.version + config.description())

REGISTRY.register(KibanaCollector(config.kibana_url))

root = Resource()
root.putChild(b'metrics', MetricsResource(registry=REGISTRY))
factory = Site(root)
reactor.listenTCP(config.listen_port, factory)
reactor.run()
