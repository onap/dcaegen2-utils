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

import json
import docker
import requests
from dockering.exceptions import DockerError, DockerConnectionError
from dockering import config_building as cb
from dockering import utils


def create_client(hostname, port, reauth=False, logins=[]):
    """Create Docker client

    Args:
    -----
    reauth: (boolean) Forces reauthentication e.g. Docker login
    """
    base_url = "tcp://{0}:{1}".format(hostname, port)
    try:
        client = docker.Client(base_url=base_url)

        for dcl in logins:
            dcl["reauth"] = reauth
            client.login(**dcl)

        return client
    except requests.exceptions.ConnectionError as e:
        raise DockerConnectionError(str(e))


def create_container_using_config(client, service_component_name, container_config):
    try:
        image_name = container_config["Image"]

        if not client.images(image_name):
            def parse_pull_response(response):
                """Pull response is a giant string of JSON messages concatentated
                by `\r\n`. This method returns back those messages in the form of
                list of dicts."""
                # NOTE: There's a trailing `\r\n` so the last element is empty
                # string. Remove that.
                return list(map(json.loads, response.split("\r\n")[:-1]))

            def get_error_message(response):
                """Attempts to pull out and return an error message from parsed
                response if it exists else return None"""
                return response[-1].get("error", None)

            # TODO: Implement this as verbose?
            # for resp in client.pull(image, stream=True, decode=True):
            response = parse_pull_response(client.pull(image_name))
            error_message = get_error_message(response)

            if error_message:
                raise DockerError("Error pulling Docker image: {0}".format(error_message))
            else:
                utils.logger.info("Pulled Docker image: {0}".format(image_name))

        return client.create_container_from_config(container_config,
                service_component_name)
    except requests.exceptions.ConnectionError as e:
        # This separates connection failures so that caller can decide what to do.
        # Underlying errors this inspired were socket.errors that are sourced
        # from http://www.virtsync.com/c-error-codes-include-errno
        raise DockerConnectionError(str(e))
    except Exception as e:
        raise DockerError(str(e))


def create_container(client, image_name, service_component_name, envs,
        host_config_params):
    """Creates Docker container

    Args:
    -----
    envs (dict): dict of environment variables to pass into the docker containers.
        Gets passed into docker-py.create_container call
    host_config_params (dict): Dict of input parameters to the docker-py
        "create_host_config" method call
    """
    config = cb.create_container_config(client, image_name, envs, host_config_params)
    return create_container_using_config(client, service_component_name, config)


def start_container(client, container):
    try:
        # TODO: Have logic to inspect response and through NonRecoverableError
        # when start fails. Docker-py docs don't quickly tell me what the
        # response looks like.
        response = client.start(container=container["Id"])
        utils.logger.info("Container started: {0}".format(container["Id"]))

        # TODO: Maybe check stats?
        return container["Id"]
    except Exception as e:
        raise DockerError(str(e))


def stop_then_remove_container(client, service_component_name):
    try:
        client.stop(service_component_name)
        client.remove_container(service_component_name)
    except docker.errors.NotFound as e:
        raise DockerError("Container not found: {0}".format(service_component_name))
    except Exception as e:
        raise DockerError(str(e))


def remove_image(client, image_name):
    """Remove the Docker image"""
    try:
        client.remove_image(image_name)
        return True
    except:
        # Failure to remove image is not classified as terrible..for now
        return False


def build_policy_update_cmd(script_path, use_sh=True, msg_type="policy", **kwargs):
    """Build command to execute for policy update"""
    data = json.dumps(kwargs or {})

    if use_sh:
        return ['/bin/sh', script_path, msg_type, data]
    else:
        return [script_path, msg_type, data]

def notify_for_policy_update(client, container_id, cmd):
    """Notify Docker container that policy update occurred

    Notify the Docker container by doing Docker exec of passed-in command

    Args:
    -----
    container_id: (string)
    cmd: (list) of strings each entry being part of the command
    """
    try:
        result = client.exec_create(container=container_id,
                cmd=cmd)
        result = client.exec_start(exec_id=result['Id'])

        utils.logger.info("Pass to docker exec {0} {1} {2}".format(
            container_id, cmd, result))

        return result
    except Exception as e:
        raise DockerError(e)
