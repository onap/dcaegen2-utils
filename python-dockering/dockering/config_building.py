# org.onap.dcae
# ================================================================================
# Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END=========================================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.

"""
Abstraction in Docker container configuration
"""
import six
from dockering import utils
from dockering.exceptions import DockerConstructionError


#
# Methods to build container envs
#

def create_envs_healthcheck(docker_config, default_interval="15s",
        default_timeout="1s"):
    """Extract health check environment variables for Docker containers

    Parameters
    ----------
    docker_config: dict where there's an entry called "healthcheck"

    Returns
    -------
    dict of Docker envs for healthcheck
    """
    # TODO: This has been shamefully lifted from the dcae-cli and should probably
    # shared as a library. The unit tests are there. The difference is that
    # there are defaults that are passed in here but the defaults should really
    # come from the component spec definition. The issue is that nothing forwards
    # those defaults.

    envs = dict()
    hc = docker_config["healthcheck"]

    # NOTE: For the multiple port, schema scenario, you can explicitly set port
    # to schema. For example if image EXPOSE 8080, SERVICE_8080_CHECK_HTTP works.
    # https://github.com/gliderlabs/registrator/issues/311

    if hc["type"] == "http":
        envs["SERVICE_CHECK_HTTP"] = hc["endpoint"]
    elif hc["type"] == "https":
        # WATCH: HTTPS health checks don't work. Seems like Registrator bug.
        # Submitted issue https://github.com/gliderlabs/registrator/issues/516
        envs["SERVICE_CHECK_HTTPS"] = hc["endpoint"]
        utils.logger.warn("Https-based health checks may not work because Registrator issue #516")
    elif hc["type"] == "script":
        envs["SERVICE_CHECK_SCRIPT"] = hc["script"]
    elif hc["type"] == "docker":
        # Note this is only supported in the AT&T open source version of registrator
        envs["SERVICE_CHECK_DOCKER_SCRIPT"] = hc["script"]
    else:
        # You should never get here but not having an else block feels weird
        raise DockerConstructionError("Unexpected health check type: {0}".format(hc["type"]))

    envs["SERVICE_CHECK_INTERVAL"] = hc.get("interval", default_interval)
    envs["SERVICE_CHECK_TIMEOUT"] = hc.get("timeout", default_timeout)

    return envs


def create_envs(service_component_name, *envs):
    """Merge all environment variables maps

    Creates a complete environment variables map that is to be used for creating
    the container.

    Args:
    -----
    envs: Arbitrary list of dicts where each dict is of the structure:

        {
            <environment variable name>: <environment variable value>,
            <environment variable name>: <environment variable value>,
            ...
        }

    Returns:
    --------
    Dict of all environment variable name to environment variable value
    """
    master_envs = { "HOSTNAME": service_component_name,
                    # For Registrator to register with generated name and not the
                    # image name
                    "SERVICE_NAME": service_component_name }
    for envs_map in envs:
        master_envs.update(envs_map)
    return master_envs


#
# Methods for volume bindings
#

def _parse_volumes_param(volumes):
    """Parse volumes details for Docker containers from blueprint

    Takes in a list of dicts that contains Docker volume info and
    transforms them into docker-py compliant (unflattened) data structures.
    Look for the `volumes` parameters under the `run` method on
    [this page](https://docker-py.readthedocs.io/en/stable/containers.html)

    Args:
        volumes (list): List of

            {
              "host": {
                "path": <target path on host>
                },
              "container": {
                "bind": <target path in container>,
                "mode": <read/write>
              }
            }

    Returns:
        dict of the form

            {
              <target path on host>: {
                "bind": <target path in container>,
                "mode": <read/write>
              }
            }

        if volumes is None then returns None
    """
    if volumes:
        return dict([ (vol["host"]["path"], vol["container"]) for vol in volumes ])
    else:
        return None


#
# Utility methods used to help build the inputs to create the host_config
#

def add_host_config_params_volumes(volumes=None, host_config_params=None):
    """Add volumes input params

    Args:
    -----
    volumes (list): List of

            {
              "host": {
                "path": <target path on host>
                },
              "container": {
                "bind": <target path in container>,
                "mode": <read/write>
              }
            }

    host_config_params (dict): Target dict to accumulate host config inputs

    Returns:
    --------
    Updated host_config_params
    """
# TODO: USE parse_volumes_param here!
    if host_config_params == None:
        host_config_params = {}

    host_config_params["binds"] = _parse_volumes_param(volumes)
    return host_config_params

def add_host_config_params_ports(ports=None, host_config_params=None):
    """Add ports input params

    Args:
    -----
    ports (list): Each port mapping entry is of the form

        "<container ports>:<host port>"

    host_config_params (dict): Target dict to accumulate host config inputs

    Returns:
    --------
    Updated host_config_params
    """
    if host_config_params == None:
        host_config_params = {}

    if ports:
        ports = [ port.split(":") for port in ports ]
        port_bindings = { port[0]: { "HostPort": port[1] }  for port in ports }
        host_config_params["port_bindings"] = port_bindings
        host_config_params["publish_all_ports"] = False
    else:
        host_config_params["publish_all_ports"] = True

    return host_config_params

def add_host_config_params_dns(docker_host, host_config_params=None):
    """Add dns input params

    This is not a generic implementation. This method will setup dns with the
    expectation that a local consul agent is running on the docker host and will
    service the dns requests.

    Args:
    -----
    docker_host (string): Docker host ip address which will be used as the dns server
    host_config_params (dict): Target dict to accumulate host config inputs

    Returns:
    --------
    Updated host_config_params
    """
    if host_config_params == None:
        host_config_params = {}

    host_config_params["dns"] = [docker_host]
    host_config_params["dns_search"] = ["service.consul"]
    host_config_params["extra_hosts"] = { "consul": docker_host }
    return host_config_params


def _get_container_ports(host_config_params):
    """Grab list of container ports from host config params"""
    if "port_bindings" in host_config_params:
        return list(six.iterkeys(host_config_params["port_bindings"]))
    else:
        return None

def create_container_config(client, image, envs, host_config_params, tty=False):
    """Create docker container config

    Args:
    -----
    envs (dict): dict of environment variables to pass into the docker containers.
        Gets passed into docker-py.create_container call
    host_config_params (dict): Dict of input parameters to the docker-py
        "create_host_config" method call
    """
    # This is the 1.10.6 approach to binding volumes
    # http://docker-py.readthedocs.io/en/1.10.6/volumes.html
    volumes = host_config_params.get("bind", None)
    target_volumes = [ target["bind"] for target in volumes.values() ] \
            if volumes else None

    host_config = client.create_host_config(**host_config_params)

    ports = _get_container_ports(host_config_params)

    command = "" # This is required...
    config = client.create_container_config(image, command, detach=True, tty=tty,
            host_config=host_config, ports=ports,
            environment=envs, volumes=target_volumes)

    utils.logger.info("Docker container config: {0}".format(config))

    return config

