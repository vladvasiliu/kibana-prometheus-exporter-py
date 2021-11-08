[![Scrutinizer code quality](https://img.shields.io/scrutinizer/g/vladvasiliu/kibana-prometheus-exporter-py.svg)](https://scrutinizer-ci.com/g/vladvasiliu/kibana-prometheus-exporter-py/)
[![License](https://img.shields.io/github/license/vladvasiliu/kibana-prometheus-exporter-py.svg)](COPYING)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# kibana-prometheus-exporter

This is a Prometheus exporter for Kibana written in Python.

See the [changelog](CHANGELOG.md).

## Usage

### Configuration

Configuration is done via environment variables. Available parameters:

|Parameter          |Default|Required|
|-------------------|-------|--------|
|KIBANA_URL         |-      |Yes     |
|LISTEN_PORT        |9563   |No      |
|LOG_LEVEL          |INFO   |No      |
|KIBANA_LOGIN       |-      |No      |
|KIBANA_PASSWORD    |-      |No      |
|IGNORE_SSL         |FALSE  |No      |
|REQUESTS_CA_BUNDLE |-      |No      |

Authentication can also be done via a netrc file. `requests` natively supports this.

You can provide CA bundle for `requests` library using the `REQUESTS_CA_BUNDLE` environment variable

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

Install the dependencies:

    pip install -r requirements.txt

Run the program specifying options:

    KIBANA_URL="https://your_kibana_node.com" python kibana_prometheus_exporter


#### Docker

A docker container is hosted [on GitHub Packages](https://github.com/vladvasiliu/kibana-prometheus-exporter-py/pkgs/container/kibana-prometheus-exporter-py). To run it:

    docker run -d -p 9563:9563 --name kibana_exporter -e KIBANA_URL="https://your_kibana_node.com" ghcr.io/vladvasiliu/kibana-prometheus-exporter-py:latest


## Known issues and limitations

### All metrics are gauges

The exporter reads data from the Kibana Stats API. This API only provides "real time" metrics, refreshed every 5 seconds.
As such, some metrics which usually are counters can only be gauges (eg `kibana_requests_total`).

See below for how Kibana handles this internally :

* [PR that replaces accumulating counters](https://github.com/elastic/kibana/pull/20577/files#r202416647)
* [Source code](https://github.com/elastic/kibana/blob/master/src/legacy/server/status/collectors/get_ops_stats_collector.js#L27)

A possible workaround is setting Kibana `ops.interval` to the same value as the scrape interval
and using the statistics timestamp from the response as the Prometheus timestamp.

### Missing metrics

I have noticed since the update to Kibana 6.7 that sometimes the avg request time is missing from the stats dictionary.
[Source](https://github.com/elastic/kibana/blob/6.7/src/server/status/lib/metrics.js#L73)

The reason is probably a division by 0 when there are no requests during the sampling interval.
I think it's better to set the value to 0 then to have a gap  in the time series.


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
