This is a Prometheus exporter for Kibana written in Python.

It's strongly inspired by [Kibana Prometheus Exporter](https://github.com/pjhampton/kibana-prometheus-exporter). There are two main reasons I've done this :

* Since version 6 there have been some changes in Kibana itself that interfere with this plugin working correctly with IPv6
* I want to have a separate exporter that doesn't need updating on every Kibana update
