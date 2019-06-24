# Python CBS Docker Client

Used for DCAE Dockerized microservices written in Python. Pulls your configuration from the Config Binding Service

# Client Usage

The environment that this client runs in, whether it be in Docker or "natively", needs to have the following env variables:
1. `HOSTNAME` is the name of your component in Consul
2. `CONFIG_BINDING_SERVICE` a resolvable hostname to the CBS
3. If the CBS is running as HTTPS: `DCAE_CA_CERTPATH`: a path to a cacert file to verify the running CBS

## Usage in your code

See the `example` folder for a simple test client.

If the CBS is reachable, but your configuration key is not there, you will get a CantGetConfig exception:

    onap_dcae_cbs_docker_client.exceptions.CantGetConfig

You can access the original HTTP status code and text via the `code` and `text` attributes.

If the CBS is unreachable, you will get an exception:

    onap_dcae_cbs_docker_client.exceptions.CBSUnreachable

# Installation

## Via pip
```
pip install onap-dcae-cbs-docker-client
```

# Testing
```
tox
```

# Version Changes
When changes are made, the versions to be bumped are in:

1. setup.py
2. Changelog.md
3. pom.xml
