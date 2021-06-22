# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.2.0] 2021/06/22
* DCAEGEN2-2733/DCAEGEN2-2753 - onap-dcae-cbs-docker-client support local config and policy files
	Support $CBS_CLIENT_CONFIG_PATH and $CBS_CLIENT_POLICY_PATH,
	Default paths are /app-config/application_config.yaml and /etc/policies/policies.json.
	If files are missing or malformed, drop back to the current behavior.

## [2.1.2] - 2021/05/13
* Add service for envs present in configuration

## [2.1.1] - 2020/04/27
* Bug fix DCAEGEN2-2213 ConnectionError exception is lost when CBSUnreachable is raised

## [2.1.0] - 2019/6/24
* Add support for connecting to the CBS if it is running as HTTPS instead of HTTP

## [2.0.0] - 2019/6/19
* The env variable CONFIG_BINDING_SERVICE now has a different meaning per DCAEGEN2-1537. Specifically this variable now holds a resolvable hostname for the CBS, rather than a consul lookup key
* Since the API was broken anyway, the decision not to throw an exception was revisted and overturned. This was causing problems for some users, who were getting `{}` back in their configuration, but without knowing why; either the config wasn't set up, the config was set but as `{}`, or the CBS being unreachable altogether. This client library now throws native python exceptions, rather than logging and returning `{}`. The application client code can handle the exceptions, and retry if they choose.
* Add more tests, move fixtures to conftest
* Move exceptions to own module

## [1.0.4]
* Allow the CBS to be registered in Consul under a different name than "config_binding_service"; instead read from the already-set ENV variable CONFIG_BINDING_SERVICE

## [1.0.3]
* Fix an issue caused by flake8 upgrading

## [1.0.2]
* Refactor some code, PEP8 compliance
* Add flake8 to tox

## [1.0.1]
* [Sadly, Missing]

## [1.0.0]
* Depend on the CBS 2.0.0 API
* Add new endpoint for getting all

## [0.0.5]
* Dont pin requests version

## [0.0.3]
* Changelog started
* Unit test suite created
* Current test coverage = 82%
