# ================================================================================
# Copyright (c) 2017-2019 AT&T Intellectual Property. All rights reserved.
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
import requests
from onap_dcae_cbs_docker_client import get_module_logger
from onap_dcae_cbs_docker_client.exceptions import ENVsMissing, CantGetConfig, CBSUnreachable


logger = get_module_logger(__name__)


#########
# HELPERS
def _get_path(path):
    """
    This call does not raise an exception if Consul or the CBS cannot complete the request.
    It logs an error and returns {} if the config is not bindable.
    It could be a temporary network outage. Call me again later.

    It will raise an exception if the necessary env parameters were not set because that is irrecoverable.
    """
    try:
        hostname = os.environ["HOSTNAME"]  # this is the name of the component itself
        # in most cases, this is the K8s service name which is a resolavable DNS name
        # if running outside k8s, this name needs to be resolvable by DNS via other means.
        cbs_resolvable_hostname = os.environ["CONFIG_BINDING_SERVICE"]
    except KeyError as e:
        raise ENVsMissing("Required ENV Variable {0} missing".format(e))

    # TODO: https
    cbs_url = "http://{0}:10000".format(cbs_resolvable_hostname)

    # get my config
    try:
        my_config_endpoint = "{0}/{1}/{2}".format(cbs_url, path, hostname)
        res = requests.get(my_config_endpoint)
        res.raise_for_status()
        config = res.json()
        logger.debug(
            "get_config returned the following configuration: %s using the config url %s",
            json.dumps(config),
            my_config_endpoint,
        )
        return config
    except requests.exceptions.HTTPError:  # this is thrown by raise_for_status
        logger.error(
            "The config binding service endpoint %s returned a bad status. code: %d, text: %s",
            my_config_endpoint,
            res.status_code,
            res.text,
        )
        raise CantGetConfig()
    except requests.exceptions.ConnectionError:  # this is thrown if requests.get cant even connect to the endpoint
        raise CBSUnreachable()


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
