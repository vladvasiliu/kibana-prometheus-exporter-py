# CHANGELOG
This file documents notable changes to Kibana Prometheus Exporter starting with version 1.14.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) starting with version 1.14.1.

## 1.17.0 - 2021-11-08

* Moved container hosting to [GitHub Packages](https://github.com/vladvasiliu/kibana-prometheus-exporter-py/pkgs/container/kibana-prometheus-exporter-py)
* Upgraded dependencies
* Upgrades Docker base file to 3.9.7-alpine3.14

## 1.16.0 - 2021-01-22

* Switched Docker labels to opencontainers format
* Added pre_build hook for injecting metadata when building on Docker Hub
* Updated dependencies

## 1.15.3 - 2020-12-26

Updated dependencies. No user-facing changes are introduced.

Dockerfile is based on python3.9.1-alpine3.12

## 1.15.2 - 2020-10-25

Updated dependencies. No user-facing changes are introduced.

Dockerfile is based on python3.8.6-alpine3.12

## 1.15.1 - 2020-08-08

Updated dependencies. No user-facing changes are introduced.

Dockerfile is based on python3.8.5-alpine3.12


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
