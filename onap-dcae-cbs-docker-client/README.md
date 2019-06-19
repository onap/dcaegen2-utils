# Python CBS Docker Client

Used for DCAE Dockerized microservices written in Python. Pulls your configuration from the Config Binding Service

# Client Usage

The envrionment that this client runs in, whether it be in Docker or "natievely", needs to have the following env variables:
1. `HOSTNAME` is the name of your component in Consul
2. `CONFIG_BINDING_SERVICE` a resolvable hostname to the CBS

## Usage in your code

    >>> from onap_dcae_cbs_docker_client import client
    >>> client.get_config()
    >>> client.get_all()


If the CBS is reachable, but your configuration key is not there, you will get a CantGetConfig exception:

    onap_dcae_cbs_docker_client.exceptions.CantGetConfig


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
