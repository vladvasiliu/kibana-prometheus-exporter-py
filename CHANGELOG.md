# CHANGELOG
This file documents notable changes to Kibana Prometheus Exporter starting with version 1.14.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) starting with version 1.14.1.

## 1.15.0 - 2020-06-01
### Breaking changes
* Docker environment variable `PORT` was renamed to `LISTEN_PORT` ([issue #10](https://github.com/vladvasiliu/kibana-prometheus-exporter-py/issues/10)).
### Changes
* Configuration display now prints the log level name instead of number.
* Moved Docker labels to the final container.


## 1.14.1 - 2020-06-01
First version using SemVer.
### Changes
* Actually fix port in Dockerfile.


## 1.14 - 2020-06-01
### Changes
* Fix port in Dockerfile. See [#10](https://github.com/vladvasiliu/kibana-prometheus-exporter-py/issues/10).
* Updated prometheus_client to v0.8.0.