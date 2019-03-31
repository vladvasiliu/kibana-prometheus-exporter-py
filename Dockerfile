FROM python:3.7.3-alpine3.9

LABEL version="1.0"
LABEL description="Prometheus Kibana exporter"
LABEL maintainer="Vlad Vasiliu <vladvasiliun@yahoo.fr>"

ARG PORT=9563
EXPOSE $PORT

COPY . /code
WORKDIR /code
RUN chmod u+x src/main.py

RUN apk add --no-cache --virtual build-dependencies \
    git \
    build-base
RUN pip install pipenv &&\
    pipenv install --deploy --system --ignore-pipfile
RUN apk del build-dependencies
RUN apk add --no-cache curl

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -s http://127.0.0.1:$PORT -o /dev/null || exit 1
CMD ["python", "/code/src/main.py"]
