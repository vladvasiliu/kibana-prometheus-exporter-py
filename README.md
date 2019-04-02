[![Scrutinizer code quality](https://img.shields.io/scrutinizer/g/vladvasiliu/kibana-prometheus-exporter-py.svg)](https://scrutinizer-ci.com/g/vladvasiliu/kibana-prometheus-exporter-py/)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/vladvasiliu/kibana_exporter.svg)
[![Docker Pulls](https://img.shields.io/docker/pulls/vladvasiliu/kibana_exporter.svg)](https://hub.docker.com/r/vladvasiliu/kibana_exporter)
[![License](https://img.shields.io/github/license/vladvasiliu/kibana-prometheus-exporter-py.svg)](COPYING)


# kibana-prometheus-exporter

This is a Prometheus exporter for Kibana written in Python.

## Usage

### Configuration

Configuration is done via environment variables. Available parameters:

|Parameter      |Default|
|---------------|-------|
|KIBANA_URL     |-      |
|LISTEN_PORT    |9563   |
|LOG_LEVEL      |INFO   |
|KIBANA_LOGIN   |-      |
|KIBANA_PASSWORD|-      |

Authentication can also be done via a netrc file. `requests` natively supports this.

Documentation:
* [`requests`](http://docs.python-requests.org/en/master/user/authentication/)
* [`netrc`](https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html)


### Running

#### Dependencies

This project is developed using Python 3.7. It will likely work with all supported versions of Python 3, but it's not tested.

This project uses the following libraries:

* [Prometheus Python client](https://github.com/prometheus/client_python)
* [Requests](http://docs.python-requests.org/en/master/)
* [Twisted](https://www.twistedmatrix.com/trac/)

To install dependencies with `pipenv`:

    pipenv install --deploy

If you want to use classic `pip` instead:

    pip install -r requirements.txt

Run the program specifying options:

    KIBANA_URL="https://your_kibana_node.com" python src/main.py


#### Docker

A docker container is built and hosted [on the Docker Hub](https://pipenv.readthedocs.io/en/latest/). To run it:

    docker run -d -p 9563:9563 --name kibana_exporter -e KIBANA_URL="https://your_kibana_node.com" vladvasiliu/kibana_exporter:latest


## Known issues and limitations

### All metrics are gauges

The exporter reads data from the Kibana Stats API. This API only provides "real time" metrics, refreshed every 5 seconds.
As such, some metrics which usually are counters can only be gauges (eg `kibana_requests_total`).

See below for how Kibana handles this internally :

* [PR that replaces accumulating counters](https://github.com/elastic/kibana/pull/20577/files#r202416647)
* [Source code](https://github.com/elastic/kibana/blob/master/src/legacy/server/status/collectors/get_ops_stats_collector.js#L27)

### Missing metrics

I have noticed since the update to Kibana 6.7 that sometimes the avg request time is missing from the stats dictionary.
I'm not yet sure how to handle this.


## Contributing

Please feel free to send a PR for any changes or improvements you may have.

### Branching model

This project uses a branching model inspired by [git-flow](https://datasift.github.io/gitflow/IntroducingGitFlow.html).

* `master` should be ready to be deployed.
* `develop` is where development happens. May be unstable.
* `feature/*` is a work-in-progress on a major new feature.
* versions are tagged on master.

## Similar projects

It's strongly inspired by [Kibana Prometheus Exporter](https://github.com/pjhampton/kibana-prometheus-exporter). There are two main reasons I've done this:

* Since version 6 there have been some changes in Kibana itself that interfere with this plugin working correctly with IPv6;
* I want to have a separate exporter that doesn't need updating on every Kibana update.



## Licensing

### Author
kibana-prometheus-exporter is created by [Vlad Vasiliu](https://github.com/vladvasiliu/).

### License
This project is released under the terms of the GPLv3 license. See [`COPYING`](COPYING) for the full text.
