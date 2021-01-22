ARG BASE_IMAGE="python:3.9.1-alpine3.12"

FROM $BASE_IMAGE AS builder


RUN     apk add --no-cache --virtual build-dependencies build-base

COPY    requirements.txt /

RUN     pip install virtualenv && \
        virtualenv /venv && \
        source /venv/bin/activate && \
        pip install -r /requirements.txt

COPY    kibana_prometheus_exporter /venv/kibana_prometheus_exporter

FROM $BASE_IMAGE

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
RUN apk add --no-cache curl
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -s http://127.0.0.1:$LISTEN_PORT -o /dev/null || exit 1
WORKDIR /venv
ENTRYPOINT ["/venv/bin/python", "-m", "kibana_prometheus_exporter"]
