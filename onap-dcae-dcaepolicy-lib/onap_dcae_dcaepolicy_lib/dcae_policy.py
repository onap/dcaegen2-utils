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

"""dcae_policy contains decorators for the policy lifecycle in cloudify"""

import json
import traceback
from copy import deepcopy
from functools import wraps

from cloudify import ctx
from cloudify.context import NODE_INSTANCE
from cloudify.exceptions import NonRecoverableError

from .policies_output import PoliciesOutput

POLICIES = 'policies'
POLICY_FILTERS = 'policy_filters'
POLICIES_FILTERED = 'policies_filtered'

POLICY_ID = 'policy_id'
POLICY_BODY = 'policy_body'
POLICY_VERSION = "policyVersion"
POLICY_CONFIG = 'config'

POLICY_FILTER = 'policy_filter'
POLICY_FILTER_ID = 'policy_filter_id'

POLICY_PERSISTENT = 'policy_persistent'
DCAE_POLICY_TYPE = 'dcae.nodes.policy'
DCAE_POLICIES_TYPE = 'dcae.nodes.policies'

ACTION_GATHERED = "gathered"
ACTION_UPDATED = "updated"

CONFIG_ATTRIBUTES = "configAttributes"

class Policies(object):
    """static class for policy operations"""
    _updated_policies = {}
    _removed_policies = {}

    @staticmethod
    def _init():
        """init static members"""
        Policies._updated_policies = {}
        Policies._removed_policies = {}

    @staticmethod
    def _set_policies(policies):
        """store the :policies: in :runtime_properties[POLICIES]:"""
        if not policies:
            if POLICIES in ctx.instance.runtime_properties:
                del ctx.instance.runtime_properties[POLICIES]
            return

        ctx.instance.runtime_properties[POLICIES] = policies

    @staticmethod
    def _add_policy(policy_id, policy, policy_persistent, policies):
        """only add the latest version of policy to policies"""
        prev_policy = policies.get(policy_id)
        prev_policy_persistent = (prev_policy or {}).get(POLICY_PERSISTENT)

        if not prev_policy \
        or (policy_persistent and not prev_policy_persistent) \
        or (policy_persistent == prev_policy_persistent and policy.get(POLICY_BODY)):
            policy = deepcopy(policy)
            policy[POLICY_PERSISTENT] = policy_persistent
            policies[policy_id] = policy

    @staticmethod
    def _gather_policy(target, policies):
        """adds the policy from dcae.nodes.policy node to policies"""
        if DCAE_POLICY_TYPE not in target.node.type_hierarchy:
            return
        policy_id = target.node.properties.get(POLICY_ID)
        if not policy_id:
            return True
        policy = deepcopy(dict(target.node.properties))
        policy_body = target.instance.runtime_properties.get(POLICY_BODY)
        if policy_body:
            policy[POLICY_BODY] = policy_body

        Policies._add_policy(policy_id, policy, True, policies)
        return True

    @staticmethod
    def _fix_policy_filter(policy_filter):
        if CONFIG_ATTRIBUTES in policy_filter:
            config_attributes = policy_filter.get(CONFIG_ATTRIBUTES)
            if isinstance(config_attributes, dict):
                return
            try:
                config_attributes = json.loads(config_attributes)
                if config_attributes and isinstance(config_attributes, dict):
                    policy_filter[CONFIG_ATTRIBUTES] = config_attributes
                    return
            except (ValueError, TypeError):
                pass
            if config_attributes:
                ctx.logger.warn("unexpected %s: %s", CONFIG_ATTRIBUTES, config_attributes)
            del policy_filter[CONFIG_ATTRIBUTES]

    @staticmethod
    def _gather_policies(target, policies, policy_filters):
        """adds the policies and policy-filter from dcae.nodes.policies node to policies"""
        if DCAE_POLICIES_TYPE not in target.node.type_hierarchy:
            return

        property_policy_filter = target.node.properties.get(POLICY_FILTER)
        if property_policy_filter:
            policy_filter = deepcopy(dict(
                (k, v) for (k, v) in dict(property_policy_filter).items()
                if v or isinstance(v, (int, float))
            ))
            Policies._fix_policy_filter(policy_filter)

            if policy_filter:
                policy_filters[target.instance.id] = {
                    POLICY_FILTER_ID : target.instance.id,
                    POLICY_FILTER : policy_filter
                }

        filtered_policies = target.instance.runtime_properties.get(POLICIES_FILTERED)
        if not filtered_policies or not isinstance(filtered_policies, dict):
            return True
        for (policy_id, policy) in filtered_policies.items():
            Policies._add_policy(policy_id, policy, False, policies)
        return True

    @staticmethod
    def _get_policy_bodies_dict(policies):
        """returns a dict of policy_id -> policy_body if policy_body exists"""
        if not policies:
            return {}

        return {policy_id: policy.get(POLICY_BODY)
                for policy_id, policy in policies.items() if policy.get(POLICY_BODY)}

    @staticmethod
    def gather_policies_to_node():
        """
        decorate with @Policies.gather_policies_to_node() to
        gather the policies from dcae.nodes.policy nodes this node depends on.

        Places the policies into runtime_properties["policies"].

        Stores <scn>:policies data in consul-kv
        """
        def gather_policies_decorator(func):
            """the decorator"""
            if not func:
                return

            @wraps(func)
            def wrapper(*args, **kwargs):
                """gather and save the policies from dcae.nodes.policy nodes this node related to"""
                if ctx.type != NODE_INSTANCE:
                    raise NonRecoverableError("can only invoke gather_policies_to_node on node")

                policy_bodies = []
                try:
                    policies = {}
                    policy_filters = {}
                    for rel in ctx.instance.relationships:
                        _ = Policies._gather_policy(rel.target, policies) \
                         or Policies._gather_policies(rel.target, policies, policy_filters)

                    Policies._set_policies(policies)
                    if policy_filters:
                        ctx.instance.runtime_properties[POLICY_FILTERS] = policy_filters

                    policy_bodies = Policies._get_policy_bodies_dict(policies)
                except Exception as ex:
                    error = "Failed to set the policies {0}".format(str(ex))
                    ctx.logger.error("{0}: {1}".format(error, traceback.format_exc()))
                    raise NonRecoverableError(error)

                func_result = func(*args, **kwargs)

                if policy_bodies:
                    PoliciesOutput.store_policies(ACTION_GATHERED, policy_bodies)

                return func_result
            return wrapper
        return gather_policies_decorator

    @staticmethod
    def _update_policies(updated_policies, added_policies, removed_policies):
        """
        filter and update policies in runtime_properties
        and return the ordered filtered list of changed_policies
        """
        Policies._init()

        if not updated_policies and not removed_policies and not added_policies:
            ctx.logger.error("update_policies_on_ctx - no updated, added, or removed policies received")
            return

        updated_policies = updated_policies or []
        added_policies = added_policies or {}
        removed_policies = removed_policies or []

        ctx.logger.info("updated_policies: {0}, added_policies: {1}, removed_policies: {2}"
                        .format(json.dumps(updated_policies),
                                json.dumps(added_policies),
                                json.dumps(removed_policies)))

        policies = ctx.instance.runtime_properties.get(POLICIES, {})
        policy_filters = ctx.instance.runtime_properties.get(POLICY_FILTERS, {})

        for policy_id in removed_policies:
            removed_policy = policies.get(policy_id)
            if removed_policy and POLICY_BODY in removed_policy:
                Policies._removed_policies[policy_id] = deepcopy(removed_policy)
                if removed_policy.get(POLICY_PERSISTENT):
                    del policies[policy_id][POLICY_BODY]
                else:
                    del policies[policy_id]

        new_policies = dict((policy_id, policy)
                            for policy_filter_id in policy_filters
                            for (policy_id, policy) in added_policies.get(policy_filter_id, {})
                                                                     .get(POLICIES, {}).items())

        ctx.logger.info("new_policies: {0}".format(json.dumps(new_policies)))

        for policy_id in new_policies:
            policy = new_policies.get(policy_id)
            deployed_policy = policies.get(policy_id)
            if not deployed_policy:
                policies[policy_id] = policy
                Policies._updated_policies[policy_id] = policy
                continue
            updated_policies.append(policy)

        skipped = {"ignored": [], "unexpected": [], "same": [], "duplicate": []}
        for policy in updated_policies:
            policy_id = policy.get(POLICY_ID)
            if not policy_id or policy_id not in policies:
                skipped["ignored"].append(policy)
                continue

            if policy_id in Policies._updated_policies:
                skipped["duplicate"].append(policy)
                continue

            updated_policy_body = policy.get(POLICY_BODY, {})
            updated_policy_version = updated_policy_body.get(POLICY_VERSION)
            if not updated_policy_version or POLICY_CONFIG not in updated_policy_body:
                skipped["unexpected"].append(policy)
                continue

            deployed_policy = policies.get(policy_id)
            deployed_policy_version = deployed_policy.get(POLICY_BODY, {}).get(POLICY_VERSION)
            if updated_policy_version == deployed_policy_version:
                skipped["same"].append(policy)
                continue

            policies[policy_id][POLICY_BODY] = updated_policy_body
            Policies._updated_policies[policy_id] = policy

        if skipped["same"] or skipped["ignored"] or skipped["unexpected"] or skipped["duplicate"]:
            ctx.logger.info("skipped updates on policies: {0}".format(json.dumps(skipped)))

        if Policies._updated_policies or Policies._removed_policies:
            Policies._set_policies(policies)
            policy_bodies = Policies._get_policy_bodies_dict(policies)
            PoliciesOutput.store_policies(ACTION_UPDATED, policy_bodies)

    @staticmethod
    def update_policies_on_node():
        """
        decorate each policy_update operation with @Policies.update_policies_on_node() to
        filter out the updated_policies to only what applies to the current node instance,
        update runtime_properties["policies"]

        updates <scn>:policies data in consul-kv

        Passes through the filtered list of updated_policies that apply to the current node instance

        :updated_policies: contains the list of changed policy_bodies

        :removed_policies: contains the list of removed policy_bodies

        :policies: contains the list of current policy_bodies
        """
        def update_policies_decorator(func):
            """actual decorator"""
            if not func:
                return

            @wraps(func)
            def wrapper(updated_policies=None, added_policies=None, removed_policies=None, **kwargs):
                """update matching policies on the node"""
                if ctx.type != NODE_INSTANCE:
                    raise NonRecoverableError("can only invoke update_policies_on_node on node")

                try:
                    Policies._update_policies(updated_policies, added_policies, removed_policies)

                    updated_policies = Policies.get_policy_bodies(
                        selected_policies=Policies._updated_policies
                    )

                    removed_policies = Policies.get_policy_bodies(
                        selected_policies=Policies._removed_policies
                    )

                except Exception as ex:
                    error = "Failed to update the policies {0}".format(str(ex))
                    ctx.logger.error("{0}: {1}".format(error, traceback.format_exc()))
                    raise NonRecoverableError(error)

                if updated_policies or removed_policies:
                    return func(updated_policies,
                                removed_policies=removed_policies,
                                policies=Policies.get_policy_bodies(),
                                **kwargs)
            return wrapper
        return update_policies_decorator

    @staticmethod
    def cleanup_policies_on_node(func):
        """
        decorate each delete operation with @Policies.cleanup_policies_on_node to
        remove <scn>:policies data in consul-kv
        """
        if not func:
            return

        @wraps(func)
        def wrapper(**kwargs):
            """remove policies in consul-kv"""
            if ctx.type == NODE_INSTANCE:
                try:
                    PoliciesOutput.delete_policies()
                except Exception as ex:
                    error = "Failed to cleanup policies in consul-kv {0}".format(str(ex))
                    ctx.logger.error("{0}: {1}".format(error, traceback.format_exc()))

            return func(**kwargs)
        return wrapper

    @staticmethod
    def get_policy_bodies(selected_policies=None):
        """returns the list of policy_body objects if policy_body exists"""
        if isinstance(selected_policies, dict):
            return deepcopy([policy.get(POLICY_BODY)
                             for policy in selected_policies.itervalues() if policy.get(POLICY_BODY)])

        policies = ctx.instance.runtime_properties.get(POLICIES, {})
        return deepcopy([policy.get(POLICY_BODY)
                         for policy in policies.itervalues() if policy.get(POLICY_BODY)])
