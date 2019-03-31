FROM python:3.7.3-alpine3.9

LABEL version="1.0"
LABEL description="Prometheus Kibana exporter"
LABEL maintainer="Vlad Vasiliu <vladvasiliun@yahoo.fr>"

EXPOSE 9563

COPY . /code
WORKDIR /code
RUN chmod u+x src/main.py

RUN apk add --no-cache \
    curl \
    git \
    build-base
RUN pip install pipenv &&\
    pipenv install --deploy --system --ignore-pipfile
RUN apk del \
    git \
    build-base

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -s http://127.0.0.1:9563 -o /dev/null || exit 1
CMD ["python", "/code/src/main.py"]
