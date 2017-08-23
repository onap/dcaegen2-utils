# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.0]

* Update `get_configuration` to use the config binding service and also use the `CONSUL_HOST` environment variable

## [2.0.0]

* Added public `resolve_name` method used to resolve names by looking up in Consul
* Changed `_resolve_name` to return lists over an arbitrary entry from the list
* Changed the `register_for_discovery` method to pass in service ip and avoid unimpressive auto ip discovery
* Changed setup.py to use abstract requirements to be a more friendly library
