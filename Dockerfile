FROM python:3.7.3-alpine3.9 AS builder

LABEL version="1.9"
LABEL description="Kibana Prometheus exporter"
LABEL maintainer="Vlad Vasiliu <vladvasiliun@yahoo.fr>"

ARG PORT=9563
EXPOSE $PORT


RUN     apk add --no-cache --virtual build-dependencies build-base

COPY    requirements.txt /

RUN     pip install virtualenv && \
        virtualenv /venv && \
        source /venv/bin/activate && \
        pip install -r /requirements.txt

COPY    kibana_prometheus_exporter /venv/kibana_prometheus_exporter

FROM python:3.7.3-alpine3.9
COPY --from=builder /venv /venv
RUN apk add --no-cache curl
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -s http://127.0.0.1:$PORT -o /dev/null || exit 1
ENTRYPOINT ["/venv/bin/python", "/venv/kibana_prometheus_exporter"]
