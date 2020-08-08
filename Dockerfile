FROM python:3.8.5-alpine3.12 AS builder




RUN     apk add --no-cache --virtual build-dependencies build-base

COPY    requirements.txt /

RUN     pip install virtualenv && \
        virtualenv /venv && \
        source /venv/bin/activate && \
        pip install -r /requirements.txt

COPY    kibana_prometheus_exporter /venv/kibana_prometheus_exporter

FROM python:3.8.5-alpine3.12

LABEL version="1.15.1"
LABEL description="Kibana Prometheus exporter"
LABEL maintainer="Vlad Vasiliu <vladvasiliun@yahoo.fr>"

ENV LISTEN_PORT 9563
EXPOSE $LISTEN_PORT

COPY --from=builder /venv /venv
RUN apk add --no-cache curl
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -s http://127.0.0.1:$LISTEN_PORT -o /dev/null || exit 1
WORKDIR /venv
ENTRYPOINT ["/venv/bin/python", "-m", "kibana_prometheus_exporter"]
