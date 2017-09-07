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

import os
from functools import partial
import pytest
import docker
from dockering import core as doc
from dockering.exceptions import DockerError, DockerConnectionError


@pytest.mark.skip(reason="Need to automatically setup Docker engine and maybe Consul")
def test_create_client():
    # Bad - Could not connect to docker engine

    with pytest.raises(DockerConnectionError):
        doc.create_client("fake", 2376, reauth=True)


# TODO: Does pytest provide an env file?
CONSUL_HOST = os.environ.get("CONSUL_HOST")
EXTERNAL_IP = os.environ.get("EXTERNAL_IP")

@pytest.mark.skip(reason="Need to automatically setup Docker engine and maybe Consul")
def test_create_container():
    client = doc.create_client("127.0.0.1", 2376)

    scn = "unittest-registrator"
    consul_host = CONSUL_HOST
    # TODO: This may not work until we push the custom registrator into DockerHub
    image_name = "registrator:latest"
    envs = { "CONSUL_HOST": CONSUL_HOST,
             "EXTERNAL_IP": EXTERNAL_IP }
    volumes = {'/var/run/docker.sock': {'bind': '/tmp/docker.sock', 'mode': 'ro'}}

    hcp = doc.add_host_config_params_volumes(volumes=volumes)
    container = doc.create_container(client, image_name, scn, envs, hcp)

    # Container is a dict with "Id". Check if container name matches scn.

    try:
        inspect_result = client.inspect_container(scn)
        import pprint
        pprint.pprint(inspect_result)

        actual_mounts = inspect_result["Mounts"][0]
        assert actual_mounts["Destination"] == volumes.values()[0]["bind"]
        assert actual_mounts["Source"] == volumes.keys()[0]
    except Exception as e:
        raise e
    finally:
        # Execute teardown/cleanup
        try:
            doc.stop_then_remove_container(client, scn)
        except:
            print("Container removal failed")


def test_build_policy_update_cmd():
    assert ["/bin/sh", "/bin/foo", "policy", "{}"] == doc.build_policy_update_cmd("/bin/foo")
    assert ["/bin/foo", "policy", "{}"] == doc.build_policy_update_cmd("/bin/foo", use_sh=False)

    kwargs = { "bar": "baz" }

    assert ["/bin/foo", "policy", "{\"bar\": \"baz\"}"] == doc.build_policy_update_cmd(
            "/bin/foo", use_sh=False, **kwargs)

    assert ["/bin/foo", "policy", "{\"application_config\": {\"key\": \"hello world\"}}"] \
        == doc.build_policy_update_cmd("/bin/foo", use_sh=False,
                application_config={"key": "hello world"})


