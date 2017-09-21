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
import copy
from functools import wraps

from cloudify import ctx
from cloudify.context import NODE_INSTANCE
from cloudify.exceptions import NonRecoverableError

POLICIES = 'policies'

POLICY_ID = 'policy_id'
POLICY_BODY = 'policy_body'
POLICY_VERSION = "policyVersion"
POLICY_CONFIG = 'config'
DCAE_POLICY_TYPE = 'dcae.nodes.policy'
POLICY_MESSAGE_TYPE = 'policy'

class Policies(object):
    """static class for policy operations"""

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
                    if configs_only:
                        updated_policies = [policy[POLICY_BODY][POLICY_CONFIG] \
                                            for policy in updated_policies \
                                                if POLICY_BODY in policy \
                                                and POLICY_CONFIG in policy[POLICY_BODY] \
                                           ]
                    return func(updated_policies, **kwargs)
            return wrapper
        return update_policies_decorator


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
