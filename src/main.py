import os
import sys

from prometheus_client.twisted import MetricsResource
from prometheus_client.core import REGISTRY
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from kibana_collector import KibanaCollector

DEFAULT_PORT = 9563

if __name__ == '__main__':
    url = os.getenv('KIBANA_URL')
    port = os.getenv('EXPORTER_PORT', DEFAULT_PORT)
    if not url:
        sys.exit(1)

    REGISTRY.register(KibanaCollector(url))

    root = Resource()
    root.putChild(b'metrics', MetricsResource(registry=REGISTRY))
    factory = Site(root)
    reactor.listenTCP(8000, factory)
    reactor.run()
