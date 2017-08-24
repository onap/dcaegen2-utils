"""client to talk to consul on standard port 8500"""

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

import requests

CONSUL_HOST = "localhost"
CONSUL_PORT = 8500

class ConsulClient(object):
    """talking to the local Consul agent for interfacing with Consul from the plugin.
    Safe to assume that the Consul agent is always at localhost.
    """
    CONSUL_SERVICE_MASK = "{0}/v1/catalog/service/{1}"
    SERVICE_MASK = "http://{0}:{1}"
    _consul_url = "http://{0}:{1}".format(CONSUL_HOST, CONSUL_PORT)

    @staticmethod
    def get_service_url(service_name):
        """find the service record in consul"""
        response = requests.get(ConsulClient.CONSUL_SERVICE_MASK.format( \
            ConsulClient._consul_url, service_name))
        response.raise_for_status()
        resp_json = response.json()
        if resp_json:
            service = resp_json[0]
            return ConsulClient.SERVICE_MASK.format( \
                    service["ServiceAddress"], service["ServicePort"])
