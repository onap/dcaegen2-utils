# ================================================================================
# Copyright (c) 2017-2018 AT&T Intellectual Property. All rights reserved.
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
import os
import logging
import requests

LOGGER = logging.getLogger().getChild(__name__)


class ENVsMissing(Exception):
    """
    Exception to represent critical ENVs are missing
    """
    pass


#########
# HELPERS


def _get_uri_from_consul(consul_url, name):
    """
    Call consul's catalog
    TODO: currently assumes there is only one service with this hostname
    """
    url = "{0}/v1/catalog/service/{1}".format(consul_url, name)
    LOGGER.debug("Trying to lookup service: {0}".format(url))
    res = requests.get(url)
    res.raise_for_status()
    services = res.json()
    return "http://{0}:{1}".format(services[0]["ServiceAddress"], services[0]["ServicePort"])


def _get_envs():
    """
    Returns hostname, consul_host.
    If the necessary ENVs are not found, this is fatal, and raises an exception.
    """
    if "HOSTNAME" not in os.environ or "CONSUL_HOST" not in os.environ:
        raise ENVsMissing("HOSTNAME or CONSUL_HOST missing")
    hostname = os.environ["HOSTNAME"]
    consul_host = os.environ["CONSUL_HOST"]
    return hostname, consul_host


def _get_path(path):
    """
    This call does not raise an exception if Consul or the CBS cannot complete the request.
    It logs an error and returns {} if the config is not bindable.
    It could be a temporary network outage. Call me again later.

    It will raise an exception if the necessary env parameters were not set because that is irrecoverable.
    This function is called in my /heatlhcheck, so this will be caught early.
    """

    config = {}

    hostname, consul_host = _get_envs()

    # not sure how I as the component developer is supposed to know consul port
    consul_url = "http://{0}:8500".format(consul_host)

    try:
        # get my config
        cbs_url = _get_uri_from_consul(consul_url, "config_binding_service")
        my_config_endpoint = "{0}/{1}/{2}".format(cbs_url, path, hostname)
        res = requests.get(my_config_endpoint)

        res.raise_for_status()
        config = res.json()
        LOGGER.info("get_config returned the following configuration: {0}".format(
            json.dumps(config)))
    except requests.exceptions.HTTPError:
        LOGGER.error("in get_config, the config binding service endpoint %s was not reachable. Error code: %d, Error text: %s", my_config_endpoint, res.status_code, res.text)
    except Exception as exc:
        LOGGER.exception(exc)
    return config


#########
# Public
def get_all():
    """
    Hit the CBS service_component_all endpoint
    """
    return _get_path("service_component_all")


def get_config():
    """
    Hit the CBS service_component endpoint
    """
    return _get_path("service_component")
