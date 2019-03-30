import os
import sys

from prometheus_client.twisted import MetricsResource
from prometheus_client.core import REGISTRY
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from kibana_collector import KibanaCollector

DEFAULT_PORT = 9563

kibana_url = os.getenv('KIBANA_URL')
if not kibana_url:
    sys.exit(1)

exporter_port = os.getenv('EXPORTER_PORT', DEFAULT_PORT)

REGISTRY.register(KibanaCollector(kibana_url))

root = Resource()
root.putChild(b'metrics', MetricsResource(registry=REGISTRY))
factory = Site(root)
reactor.listenTCP(exporter_port, factory)
reactor.run()
