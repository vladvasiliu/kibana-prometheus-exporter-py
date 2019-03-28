# kibana-prometheus-exporter

This is a Prometheus exporter for Kibana written in Python.

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
