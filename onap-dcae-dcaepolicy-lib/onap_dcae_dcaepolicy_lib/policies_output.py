# ================================================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
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

"""client to talk to consul on standard port 8500"""

import base64
import json
import urllib
import uuid
from ConfigParser import ConfigParser
from datetime import datetime

import requests
from cloudify import ctx


class PoliciesOutput(object):
    """
    static class for store-delete policies in consul kv.

    talking to consul either at
    url from the config file /opt/onap/config.txt on Cloudify Manager host
    or at http://consul:8500 or at http://localhost:8500.
    """
    CONFIG_PATH = "/opt/onap/config.txt"
    CONSUL_TXN_MASK = "http://{consul_host}/v1/txn"

    POLICIES_EVENT = 'policies_event'

    POLICIES_FOLDER_MASK = "{0}:policies/{1}"
    MAX_OPS_PER_TXN = 64

    OPERATION_SET = "set"
    OPERATION_DELETE = "delete"
    OPERATION_DELETE_FOLDER = "delete-tree"
    SERVICE_COMPONENT_NAME = "service_component_name"

    _lazy_inited = False
    _consul_hosts = None
    _txn_url = None

    @staticmethod
    def _lazy_init():
        """find out where is consul - either from config file or hardcoded 'consul'"""
        if PoliciesOutput._lazy_inited:
            return
        PoliciesOutput._lazy_inited = True
        PoliciesOutput._consul_hosts = ["consul:8500", "localhost:8500"]
        PoliciesOutput._txn_url = None

        try:
            config_parser = ConfigParser()
            if not config_parser.read(PoliciesOutput.CONFIG_PATH):
                ctx.logger.warn("not found config file at {config_path}"
                                .format(config_path=PoliciesOutput.CONFIG_PATH))
                return
            consul_host = config_parser.get('consul', 'address')
            if not consul_host:
                ctx.logger.warn("not found consul address in config file {config_path}"
                                .format(config_path=PoliciesOutput.CONFIG_PATH))
                return
            PoliciesOutput._consul_hosts.insert(0, consul_host)
            ctx.logger.info("got consul_host: {consul_host} from config file {config_path}"
                            .format(consul_host=PoliciesOutput._consul_hosts[0],
                                    config_path=PoliciesOutput.CONFIG_PATH))

        except Exception as ex:
            ctx.logger.warn("failed to get consul host from file {config_path}: {ex}"
                            .format(config_path=PoliciesOutput.CONFIG_PATH, ex=str(ex)))

    @staticmethod
    def _safe_put_to_url(url, txn):
        """safely http put transaction to consul"""
        try:
            ctx.logger.info("put to {0} txn={1}".format(url, json.dumps(txn)))
            return requests.put(url, json=txn)

        except requests.ConnectionError as ex:
            ctx.logger.warn(
                "ConnectionError - failed to put to {0}: {1} for txn={2}"
                .format(url, str(ex), json.dumps(txn))
            )
        return None


    @staticmethod
    def _safe_put_txn(txn):
        """try consul urls to safely http put transaction to consul"""
        if PoliciesOutput._txn_url:
            return PoliciesOutput._safe_put_to_url(PoliciesOutput._txn_url, txn)

        for consul_host in PoliciesOutput._consul_hosts:
            PoliciesOutput._txn_url = PoliciesOutput.CONSUL_TXN_MASK.format(consul_host=consul_host)
            response = PoliciesOutput._safe_put_to_url(PoliciesOutput._txn_url, txn)
            if response:
                return response
        return None


    @staticmethod
    def _run_transaction(operation_name, txn):
        """run a single transaction of several operations at consul /txn"""
        if not txn:
            return None

        PoliciesOutput._lazy_init()

        response = None
        try:
            response = PoliciesOutput._safe_put_txn(txn)

            if not response:
                ctx.logger.error(
                    "failed to find consul to {0} at {1} txn={2}"
                    .format(operation_name, PoliciesOutput._txn_url, json.dumps(txn)))
                return None

        except requests.exceptions.RequestException as ex:
            ctx.logger.error(
                "failed to {0} at {1}: {2} on txn={3}"
                .format(operation_name, PoliciesOutput._txn_url,
                        str(ex), json.dumps(txn)))
            return None

        if response.status_code != requests.codes.ok:
            ctx.logger.error(
                "failed {0} {1}: {2} text={3} txn={4}"
                .format(operation_name, PoliciesOutput._txn_url, response.status_code,
                        response.text, json.dumps(txn)))
            return None
        ctx.logger.info(
            "response for {0} {1}: {2} text={3} txn={4}"
            .format(operation_name, PoliciesOutput._txn_url, response.status_code,
                    response.text, json.dumps(txn)))
        return True


    @staticmethod
    def _gen_txn_operation(verb, service_component_name, key=None, value=None):
        """returns the properly formatted operation to be used inside transaction"""
        key = PoliciesOutput.POLICIES_FOLDER_MASK.format(
            service_component_name, urllib.quote(key or "")
        )
        if value:
            return {"KV": {"Verb": verb, "Key": key, "Value": base64.b64encode(value)}}
        return {"KV": {"Verb": verb, "Key": key}}


    @staticmethod
    def store_policies(action, policy_bodies):
        """put the policy_bodies for service_component_name into consul-kv"""
        service_component_name = ctx.instance.runtime_properties.get(
            PoliciesOutput.SERVICE_COMPONENT_NAME)
        if not service_component_name:
            ctx.logger.warn("failed to find service_component_name to store_policies in consul-kv")
            return False

        event = {
            "action": action,
            "timestamp": (datetime.utcnow().isoformat()[:-3] + 'Z'),
            "update_id": str(uuid.uuid4()),
            "policies_count": len(policy_bodies)
        }
        ctx.instance.runtime_properties[PoliciesOutput.POLICIES_EVENT] = event

        store_policies = [
            PoliciesOutput._gen_txn_operation(PoliciesOutput.OPERATION_SET, service_component_name,
                                              "items/" + policy_id, json.dumps(policy_body))
            for policy_id, policy_body in policy_bodies.iteritems()
        ]
        txn = [
            PoliciesOutput._gen_txn_operation(
                PoliciesOutput.OPERATION_DELETE_FOLDER, service_component_name),
            PoliciesOutput._gen_txn_operation(
                PoliciesOutput.OPERATION_SET, service_component_name, "event", json.dumps(event))
        ]
        idx_step = PoliciesOutput.MAX_OPS_PER_TXN - len(txn)
        for idx in xrange(0, len(store_policies), idx_step):
            txn += store_policies[idx : idx + idx_step]
            if not PoliciesOutput._run_transaction("store_policies", txn):
                return False
            txn = []

        PoliciesOutput._run_transaction("store_policies", txn)
        return True

    @staticmethod
    def delete_policies():
        """delete policies for service_component_name in consul-kv"""
        if PoliciesOutput.POLICIES_EVENT not in ctx.instance.runtime_properties:
            return

        service_component_name = ctx.instance.runtime_properties.get(
            PoliciesOutput.SERVICE_COMPONENT_NAME)
        if not service_component_name:
            ctx.logger.warn("failed to find service_component_name to delete_policies in consul-kv")
            return

        delete_policies = [
            PoliciesOutput._gen_txn_operation(
                PoliciesOutput.OPERATION_DELETE_FOLDER, service_component_name)
        ]
        PoliciesOutput._run_transaction("delete_policies", delete_policies)
