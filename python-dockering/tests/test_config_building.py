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

from functools import partial
import pytest
import docker
from dockering import config_building as doc
from dockering.exceptions import DockerConstructionError


# The docker-py library sneakily expects version to "know" that there is an
# actual Docker API that you can connect with.
DOCKER_API_VERSION = "auto"
HostConfig = partial(docker.types.HostConfig,
        version=DOCKER_API_VERSION)

def test_add_host_config_params_volumes():
    hcp = doc.add_host_config_params_volumes()
    hc = HostConfig(**hcp)
    expected = { 'NetworkMode': 'default' }
    assert expected == hc

    volumes = [{"host": {"path": "some-path-host"},
        "container": {"bind": "some-path-container", "mode": "ro"}}]
    hcp = doc.add_host_config_params_volumes(volumes=volumes)
    hc = HostConfig(**hcp)
    expected = {'Binds': ['some-path-host:some-path-container:ro'], 'NetworkMode': 'default'}
    assert expected == hc


def test_add_host_config_params_ports():
    ports = [ "22:22", "80:80" ]
    hcp = doc.add_host_config_params_ports(ports=ports)
    hc = HostConfig(**hcp)
    expected = {'PortBindings': {'22/tcp': [{'HostPort': '22', 'HostIp': ''}],
        '80/tcp': [{'HostPort': '80', 'HostIp': ''}]}, 'NetworkMode': 'default'}
    assert expected == hc

    hcp = doc.add_host_config_params_ports()
    hc = HostConfig(**hcp)
    expected = {'NetworkMode': 'default', 'PublishAllPorts': True}
    assert expected == hc


def test_add_host_config_params_dns():
    docker_host = "192.168.1.1"
    hcp = doc.add_host_config_params_dns(docker_host)
    hc = HostConfig(**hcp)
    expected = {'NetworkMode': 'default', 'DnsSearch': ['service.consul'],
            'Dns': ['192.168.1.1'], 'ExtraHosts': ['consul:192.168.1.1']}
    assert expected == hc


def test_create_envs_healthcheck():
    endpoint = "/foo"
    interval = "10s"
    timeout = "1s"

    docker_config = {
            "healthcheck": {
                "type": "http",
                "endpoint": endpoint,
                "interval": interval,
                "timeout": timeout
                }
            }

    expected = {
            "SERVICE_CHECK_HTTP": endpoint,
            "SERVICE_CHECK_INTERVAL": interval,
            "SERVICE_CHECK_TIMEOUT": timeout
            }

    assert expected == doc.create_envs_healthcheck(docker_config)

    docker_config["healthcheck"]["type"] = "https"
    expected = {
            "SERVICE_CHECK_HTTPS": endpoint,
            "SERVICE_CHECK_INTERVAL": interval,
            "SERVICE_CHECK_TIMEOUT": timeout,
            "SERVICE_CHECK_TLS_SKIP_VERIFY": "true"
            }

    assert expected == doc.create_envs_healthcheck(docker_config)

    # Good case for just script

    script = "/bin/boo"
    docker_config["healthcheck"]["type"] = "script"
    docker_config["healthcheck"]["script"] = script
    expected = {
            "SERVICE_CHECK_SCRIPT": script,
            "SERVICE_CHECK_INTERVAL": interval,
            "SERVICE_CHECK_TIMEOUT": timeout
            }

    assert expected == doc.create_envs_healthcheck(docker_config)

    # Good case for Docker script

    script = "/bin/boo"
    docker_config["healthcheck"]["type"] = "docker"
    docker_config["healthcheck"]["script"] = script
    expected = {
            "SERVICE_CHECK_DOCKER_SCRIPT": script,
            "SERVICE_CHECK_INTERVAL": interval,
            "SERVICE_CHECK_TIMEOUT": timeout
            }

    assert expected == doc.create_envs_healthcheck(docker_config)

    docker_config["healthcheck"]["type"] = None
    with pytest.raises(DockerConstructionError):
        doc.create_envs_healthcheck(docker_config)


def test_create_envs():
    service_component_name = "foo"
    expected_env = { "HOSTNAME": service_component_name, "SERVICE_NAME": service_component_name,
            "KEY_ONE": "value_z", "KEY_TWO": "value_y" }
    env_one = { "KEY_ONE": "value_z" }
    env_two = { "KEY_TWO": "value_y" }

    assert expected_env == doc.create_envs(service_component_name, env_one, env_two)


def test_parse_volumes_param():
    volumes = [{ "host": { "path": "/var/run/docker.sock" },
        "container": { "bind": "/tmp/docker.sock", "mode": "ro" } }]

    expected = {'/var/run/docker.sock': {'bind': '/tmp/docker.sock', 'mode': 'ro'}}
    actual = doc._parse_volumes_param(volumes)
    assert actual == expected

    assert None == doc._parse_volumes_param(None)


def test_get_container_ports():
    hcp = {'publish_all_ports': False, 'port_bindings': {'80': {'HostPort':
        '80'}, '22': {'HostPort': '22'}}}
    assert sorted(['80', '22']) == sorted(doc._get_container_ports(hcp))

    assert None == doc._get_container_ports({})
