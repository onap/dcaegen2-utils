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
import requests
import os
import logging

root = logging.getLogger()
logger = root.getChild(__name__)

#########
# HELPERS

def _get_uri_from_consul(consul_url, name):
    """
    Call consul's catalog
    TODO: currently assumes there is only one service with this HOSTNAME
    """
    url = "{0}/v1/catalog/service/{1}".format(consul_url, name)
    logger.debug("Trying to lookup service: {0}".format(url))
    res = requests.get(url)
    try:
        res.raise_for_status()
        services = res.json()
        return "http://{0}:{1}".format(services[0]["ServiceAddress"], services[0]["ServicePort"])
    except Exception as e:
        logger.error("Exception occured when querying Consul: either could not hit {0} or no service registered. Error code: {1}, Error Text: {2}".format(url, res.status_code, res.text))
        return None

def _get_envs():
    """
    Returns HOSTNAME, CONSUL_HOST, CONFIG_BINDING_SERVICE or crashes for caller to deal with
    """
    HOSTNAME = os.environ["HOSTNAME"]
    CONSUL_HOST = os.environ["CONSUL_HOST"]
    return HOSTNAME, CONSUL_HOST


#########
# Public
def get_all():
    """
    This call does not raise an exception if Consul or the CBS cannot complete the request.
    It logs an error and returns {} if the config is not bindable.
    It could be a temporary network outage. Call me again later.

    It will raise an exception if the necessary env parameters were not set because that is irrecoverable.
    This function is called in my /heatlhcheck, so this will be caught early.
    """

    config = {}

    HOSTNAME, CONSUL_HOST = _get_envs()

    #not sure how I as the component developer is supposed to know consul port
    consul_url = "http://{0}:8500".format(CONSUL_HOST)

    #get the CBS URL. Would not need the following hoorahrah if we had DNS.
    cbs_url = _get_uri_from_consul(consul_url, "config_binding_service")
    if cbs_url is None:
        logger.error("Cannot bind config at this time, cbs is unreachable")
    else:
        #get my config
        my_config_endpoint = "{0}/service_component_all/{1}".format(cbs_url, HOSTNAME)
        res = requests.get(my_config_endpoint)
        try:
            res.raise_for_status()
            config = res.json()
            logger.info("get_config returned the following configuration: {0}".format(json.dumps(config)))
        except:
            logger.error("in get_config, the config binding service endpoint {0} blew up on me. Error code: {1}, Error text: {2}".format(my_config_endpoint, res.status_code, res.text))
    return config

def get_config():
    allk = get_all()
    return allk["config"]
