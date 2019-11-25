# ================================================================================
# Copyright (c) 2019 AT&T Intellectual Property. All rights reserved.
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
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
import uuid
from datetime import datetime

import requests
from cloudify import ctx


class PoliciesOutput(object):
    """static class for store-delete policies in consul kv"""
    # it is safe to assume that consul agent is at consul:8500
    # define consul alis in /etc/hosts on cloudify manager vm
    # $ cat /etc/hosts
    # 127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4 consul
    CONSUL_TRANSACTION_URL = "http://consul:8500/v1/txn"

    POLICIES_EVENT = 'policies_event'

    POLICIES_FOLDER_MASK = "{0}:policies/{1}"
    MAX_OPS_PER_TXN = 64

    OPERATION_SET = "set"
    OPERATION_DELETE = "delete"
    OPERATION_DELETE_FOLDER = "delete-tree"
    SERVICE_COMPONENT_NAME = "service_component_name"


    @staticmethod
    def _gen_txn_operation(verb, service_component_name, key=None, value=None):
        """returns the properly formatted operation to be used inside transaction"""
        key = PoliciesOutput.POLICIES_FOLDER_MASK.format(
            service_component_name, quote(key or "")
        )
        if value:
            return {"KV": {"Verb": verb, "Key": key, "Value": base64.b64encode(value)}}
        return {"KV": {"Verb": verb, "Key": key}}


    @staticmethod
    def _run_transaction(operation_name, txn):
        """run a single transaction of several operations at consul /txn"""
        if not txn:
            return None

        response = None
        try:
            response = requests.put(PoliciesOutput.CONSUL_TRANSACTION_URL, json=txn)
        except requests.exceptions.RequestException as ex:
            ctx.logger.error(
                "RequestException - failed to {0} at {1}: {2} on txn={3}"
                .format(operation_name, PoliciesOutput.CONSUL_TRANSACTION_URL,
                        str(ex), json.dumps(txn)))
            return None

        if response.status_code != requests.codes.ok:
            ctx.logger.error(
                "failed {0} for {1} {2}: text={3} txn={4}"
                .format(response.status_code, operation_name,
                        PoliciesOutput.CONSUL_TRANSACTION_URL, response.text, json.dumps(txn)))
            return None
        ctx.logger.info(
            "response {0} for {1} {2}: text={3} txn={4}"
            .format(response.status_code, operation_name,
                    PoliciesOutput.CONSUL_TRANSACTION_URL, response.text, json.dumps(txn)))
        return True


    @staticmethod
    def store_policies(action, policy_bodies):
        """put the policy_bodies for service_component_name into consul-kv"""
        service_component_name = ctx.instance.runtime_properties.get(
            PoliciesOutput.SERVICE_COMPONENT_NAME
        )
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
            for policy_id, policy_body in policy_bodies.items()
        ]
        txn = [
            PoliciesOutput._gen_txn_operation(
                PoliciesOutput.OPERATION_DELETE_FOLDER, service_component_name),
            PoliciesOutput._gen_txn_operation(
                PoliciesOutput.OPERATION_SET, service_component_name, "event", json.dumps(event))
        ]
        idx_step = PoliciesOutput.MAX_OPS_PER_TXN - len(txn)
        for idx in range(0, len(store_policies), idx_step):
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
            PoliciesOutput.SERVICE_COMPONENT_NAME
        )
        if not service_component_name:
            ctx.logger.warn("failed to find service_component_name to delete_policies in consul-kv")
            return

        delete_policies = [
            PoliciesOutput._gen_txn_operation(
                PoliciesOutput.OPERATION_DELETE_FOLDER, service_component_name
            )
        ]
        PoliciesOutput._run_transaction("delete_policies", delete_policies)
