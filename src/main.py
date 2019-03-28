import os
import sys

from prometheus_client.twisted import MetricsResource
from prometheus_client.core import REGISTRY
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from kibana_collector import KibanaCollector


if __name__ == '__main__':
    url = os.getenv('KIBANA_URL', None)
    if not url:
        sys.exit(1)

    REGISTRY.register(KibanaCollector(url))

    root = Resource()
    root.putChild(b'metrics', MetricsResource(registry=REGISTRY))
    factory = Site(root)
    reactor.listenTCP(8000, factory)
    reactor.run()
