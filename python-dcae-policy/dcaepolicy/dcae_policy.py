"""dcae_policy contains decorators for the policy lifecycle in cloudify"""

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
import uuid
import copy
from functools import wraps

import requests

from cloudify import ctx
from cloudify.context import NODE_INSTANCE
from cloudify.exceptions import NonRecoverableError

from .dcae_consul_client import ConsulClient

POLICIES = 'policies'
SERVICE_NAME_POLICY_HANDLER = "policy_handler"
X_ECOMP_REQUESTID = 'X-ECOMP-RequestID'

POLICY_ID = 'policy_id'
POLICY_APPLY_MODE = 'policy_apply_mode'
POLICY_BODY = 'policy_body'
POLICY_VERSION = "policyVersion"
POLICY_CONFIG = 'config'
DCAE_POLICY_TYPE = 'dcae.nodes.policy'
POLICY_MESSAGE_TYPE = 'policy'
POLICY_NOTIFICATION_SCRIPT = 'script'

class Policies(object):
    """static class for policy operations"""
    _policy_handler_url = None

    @staticmethod
    def _get_latest_policy(policy_id):
        """retrieve the latest policy for policy_id from policy-handler"""
        if not Policies._policy_handler_url:
            Policies._policy_handler_url = ConsulClient.get_service_url(SERVICE_NAME_POLICY_HANDLER)

        ph_path = "{0}/policy_latest/{1}".format(Policies._policy_handler_url, policy_id)
        headers = {X_ECOMP_REQUESTID: str(uuid.uuid4())}

        ctx.logger.info("getting latest policy from {0} headers={1}".format( \
            ph_path, json.dumps(headers)))
        res = requests.get(ph_path, headers=headers)
        res.raise_for_status()

        if res.status_code == requests.codes.ok:
            return res.json()
        return {}

    @staticmethod
    def populate_policy_on_node(func):
        """dcae.nodes.policy node retrieves the policy_body identified by policy_id property
        from policy-handler that gets it from policy-engine.

        Places the found policy into runtime_properties["policy_body"].
        """
        if not func:
            return

        @wraps(func)
        def wrapper(*args, **kwargs):
            """retrieve and save the latest policy body per policy_id"""
            try:
                if ctx.type != NODE_INSTANCE:
                    return func(*args, **kwargs)

                if POLICY_ID not in ctx.node.properties:
                    ctx.logger.error("no {0} found in ctx.node.properties".format(POLICY_ID))
                    return func(*args, **kwargs)

                policy_id = ctx.node.properties[POLICY_ID]
                policy = Policies._get_latest_policy(policy_id)
                if policy:
                    ctx.logger.info("found policy {0}".format(json.dumps(policy)))
                    if POLICY_BODY in policy:
                        ctx.instance.runtime_properties[POLICY_BODY] = policy[POLICY_BODY]
                else:
                    error = "policy not found for policy_id {0}".format(policy_id)
                    ctx.logger.error(error)
                    raise NonRecoverableError(error)

            except Exception as ex:
                error = "Failed to get the policy {0}".format(str(ex))
                ctx.logger.error(error)
                raise NonRecoverableError(error)

            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def gather_policies_to_node(func):
        """decorate with @Policies.gather_policies_to_node to
        gather the policies from dcae.nodes.policy nodes this node depends on.

        Places the policies into runtime_properties["policies"].

        Call Policies.shallow_merge_policies_into(config) to merge the policies into config.
        """
        def _merge_policy_with_node(target):
            """get all properties of the policy node and add the actual policy"""
            policy = dict(target.node.properties)
            if POLICY_BODY in target.instance.runtime_properties:
                policy[POLICY_BODY] = target.instance.runtime_properties[POLICY_BODY]
            return policy

        if not func:
            return

        @wraps(func)
        def wrapper(*args, **kwargs):
            """gather and save the policies from dcae.nodes.policy nodes this node related to"""
            try:
                if ctx.type == NODE_INSTANCE:
                    policies = dict([(rel.target.node.properties[POLICY_ID], \
                                    _merge_policy_with_node(rel.target)) \
                                for rel in ctx.instance.relationships \
                                    if DCAE_POLICY_TYPE in rel.target.node.type_hierarchy \
                                    and POLICY_ID in rel.target.node.properties \
                                    and rel.target.node.properties[POLICY_ID] \
                                ])
                    if policies:
                        ctx.instance.runtime_properties[POLICIES] = policies
            except Exception as ex:
                error = "Failed to set the policies {0}".format(str(ex))
                ctx.logger.error(error)
                raise NonRecoverableError(error)

            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def _update_policies_on_ctx(updated_policies):
        """update policies in runtime_properties and return changed_policies"""
        if POLICIES not in ctx.instance.runtime_properties:
            return
        if not updated_policies:
            ctx.logger.error("update_policies_on_ctx - no updated_policies provided in arguments")
            return

        policies = ctx.instance.runtime_properties[POLICIES]
        ctx.logger.info("update_policies_on_ctx: {0}".format(json.dumps(updated_policies)))
        changed_policies = []
        ignored_policies = []
        unexpected_policies = []
        same_policies = []
        for policy in updated_policies:
            if POLICY_ID not in policy or policy[POLICY_ID] not in policies:
                ignored_policies.append(policy)
                continue
            if POLICY_BODY not in policy or POLICY_VERSION not in policy[POLICY_BODY] \
            or not policy[POLICY_BODY][POLICY_VERSION]:
                unexpected_policies.append(policy)
                continue

            deployed_policy = policies[policy[POLICY_ID]].get(POLICY_BODY, {})
            new_policy_body = policy[POLICY_BODY]
            if not deployed_policy or POLICY_VERSION not in deployed_policy \
            or not deployed_policy[POLICY_VERSION] \
            or deployed_policy[POLICY_VERSION] != new_policy_body[POLICY_VERSION]:
                policies[policy[POLICY_ID]][POLICY_BODY] = new_policy_body
                changed_policies.append(dict(policies[policy[POLICY_ID]]))
            else:
                same_policies.append(policy)

        if same_policies:
            ctx.logger.info("same policies: {0}".format(json.dumps(same_policies)))
        if ignored_policies:
            ctx.logger.info("ignored policies: {0}".format(json.dumps(ignored_policies)))
        if unexpected_policies:
            ctx.logger.warn("unexpected policies: {0}".format(json.dumps(unexpected_policies)))

        if changed_policies:
            ctx.instance.runtime_properties[POLICIES] = policies
            return changed_policies

    @staticmethod
    def update_policies_on_node(configs_only=True):
        """decorate each policy_update operation with @Policies.update_policies_on_node to
        filter out the updated_policies to only what applies to the current node instance,
        update runtime_properties["policies"]

        :configs_only: - set to True if expect to see only the config in updated_policies
            instead of the whole policy object (False)

        Passes through the filtered list of updated_policies that apply to the current node instance

        :updated_policies: contains the list of changed policy-configs when configs_only=True.

        :notify_app_through_script: in kwargs is set to True/False to indicate whether to invoke
        the script based on policy_apply_mode property in the blueprint
        """
        def update_policies_decorator(func):
            """actual decorator"""
            if not func:
                return

            @wraps(func)
            def wrapper(updated_policies, **kwargs):
                """update matching policies on context"""
                if ctx.type != NODE_INSTANCE:
                    return

                updated_policies = Policies._update_policies_on_ctx(updated_policies)
                if updated_policies:
                    notify_app_through_script = max(
                        updated_policies,
                        key=lambda pol: pol.get(POLICY_APPLY_MODE) == POLICY_NOTIFICATION_SCRIPT
                    )

                    if configs_only:
                        updated_policies = [policy[POLICY_BODY][POLICY_CONFIG] \
                                            for policy in updated_policies \
                                                if POLICY_BODY in policy \
                                                and POLICY_CONFIG in policy[POLICY_BODY] \
                                           ]
                    return func(updated_policies,
                                notify_app_through_script=notify_app_through_script, **kwargs)
            return wrapper
        return update_policies_decorator

    @staticmethod
    def get_notify_app_through_script():
        """returns True if any of the policy has property policy_apply_mode==script"""
        if ctx.type != NODE_INSTANCE \
        or POLICIES not in ctx.instance.runtime_properties:
            return
        policies = ctx.instance.runtime_properties[POLICIES]
        if not policies:
            return
        for policy_id in policies:
            if policies[policy_id].get(POLICY_APPLY_MODE) == POLICY_NOTIFICATION_SCRIPT:
                return True

    @staticmethod
    def get_policy_configs():
        """returns the list of policy configs from the runtime policies"""
        if ctx.type != NODE_INSTANCE \
        or POLICIES not in ctx.instance.runtime_properties:
            return
        policies = ctx.instance.runtime_properties[POLICIES]
        if not policies:
            return
        policy_configs = [policies[policy_id][POLICY_BODY][POLICY_CONFIG] \
                          for policy_id in policies \
                            if POLICY_BODY in policies[policy_id] \
                            and POLICY_CONFIG in policies[policy_id][POLICY_BODY] \
                         ]
        return policy_configs

    @staticmethod
    def shallow_merge_policies_into(config):
        """shallow merge the policy configs (dict) into config that is expected to be a dict"""
        if config is None:
            config = {}
        policy_configs = Policies.get_policy_configs()
        if not policy_configs or not isinstance(config, dict):
            return config

        for policy_config in copy.deepcopy(policy_configs):
            if not isinstance(policy_config, dict):
                continue

            config.update(policy_config)
            for cfg_item in policy_config:
                if policy_config[cfg_item] is None:
                    config.pop(cfg_item, None)

        return config
