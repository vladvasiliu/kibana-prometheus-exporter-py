ARG IMAGE_VERSION="3.10.9-alpine3.17"

FROM python:${IMAGE_VERSION} AS builder


RUN     apk add --no-cache --virtual build-dependencies build-base=0.5-r2

COPY    requirements.txt /

RUN     pip install --no-cache-dir virtualenv==20.17.1 && \
        virtualenv /venv && \
        /venv/bin/pip install --no-cache-dir -r /requirements.txt

COPY    kibana_prometheus_exporter /venv/kibana_prometheus_exporter

FROM python:${IMAGE_VERSION}

ARG     VERSION
ARG     BUILD_DATE
ARG     GIT_HASH

LABEL org.opencontainers.image.version="$VERSION"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.revision="$GIT_HASH"
LABEL org.opencontainers.image.title="Kibana Prometheus Exporter"
LABEL org.opencontainers.image.description="Export Kibana stats to Prometheus"
LABEL org.opencontainers.image.vendor="Vlad Vasiliu"
LABEL org.opencontainers.image.source="https://github.com/vladvasiliu/kibana-prometheus-exporter-py"
LABEL org.opencontainers.image.authors="Vlad Vasiliu and contributors"
LABEL org.opencontainers.image.url="https://github.com/vladvasiliu/kibana-prometheus-exporter-py"
LABEL org.opencontainers.image.licenses="GPL-3.0"

ENV LISTEN_PORT 9563
EXPOSE $LISTEN_PORT

COPY --from=builder /venv /venv
RUN apk add --no-cache curl=7.87.0-r0
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -s http://127.0.0.1:$LISTEN_PORT -o /dev/null || exit 1
WORKDIR /venv
ENTRYPOINT ["/venv/bin/python", "-m", "kibana_prometheus_exporter"]
