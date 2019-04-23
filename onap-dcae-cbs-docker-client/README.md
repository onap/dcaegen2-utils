# Python CBS Docker Client

Used for DCAE Dockerized microservices written in Python. Pulls your configuration from the config_binding_service. Expects that CONSUL_HOST, HOSTNAME, CONFIG_BINDING_SERVICE  are set as env variables, which is true in DCAE.

# Client Usage

## Development outside of Docker
To test your raw code without Docker, you will need to set the env variables CONSUL_HOST and HOSTNAME (name of your key to pull from) that are set in DCAEs Docker environment.
1. `CONSUL_HOST` is the hostname only of the Consul instance you are talking to
2. `HOSTNAME` is the name of your component in Consul
3. `CONFIG_BINDING_SERVICE` is the name under which the CBS is registered in Consul

## Usage in your code
```
>>> from onap_dcae_cbs_docker_client import client
>>> client.get_config()
>>> client.get_all()
```

# Installation

## Via pip
```
pip install onap-dcae-cbs-docker-client
```

# Testing
```
tox
```
