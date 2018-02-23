# org.onap.dcae
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

"""dcae_policy contains decorators for the policy lifecycle in cloudify"""

import json
import traceback
from copy import deepcopy
from functools import wraps

from cloudify import ctx
from cloudify.context import NODE_INSTANCE
from cloudify.exceptions import NonRecoverableError

from .policies_output import PoliciesOutput
from .utils import Utils

POLICIES = 'policies'
POLICY_FILTERS = 'policy_filters'
POLICIES_FILTERED = 'policies_filtered'
POLICY_APPLY_ORDER = 'policy_apply_order'
POLICY_APPLY_ORDER_CLAUSE = 'policy_apply_order_clause'
POLICY_DEFAULTED_FIELDS = 'policy_defaulted_fields'

POLICY_ID = 'policy_id'
POLICY_BODY = 'policy_body'
POLICY_VERSION = "policyVersion"
POLICY_CONFIG = 'config'
POLICY_CONFIG_CONTENT = 'content'
APPLICATION_CONFIG = 'application_config'
POLICY_FILTER = 'policy_filter'
POLICY_FILTER_ID = 'policy_filter_id'
POLICY_TYPE = 'policyType'
POLICY_TYPE_MICROSERVICE = 'MicroService'
POLICY_CONFIG_MS = "Config_MS_"

POLICY_PERSISTENT = 'policy_persistent'
DCAE_POLICY_TYPE = 'dcae.nodes.policy'
DCAE_POLICIES_TYPE = 'dcae.nodes.policies'

ACTION_GATHERED = "gathered"
ACTION_UPDATED = "updated"

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
    def _get_config_from_policy(policy):
        """returns the config field from policy object"""
        policy_body = (policy or {}).get(POLICY_BODY)
        if not policy_body:
            return

        policy_config = policy_body.get(POLICY_CONFIG)
        policy_type = policy_body.get(POLICY_TYPE)
        if not policy_type:
            policy_id = policy.get(POLICY_ID)
            if policy_id:
                policy_type_pos = policy_id.rfind(".") + 1
                if policy_type_pos and policy_id.startswith(POLICY_CONFIG_MS, policy_type_pos):
                    policy_type = POLICY_TYPE_MICROSERVICE

        if policy_type == POLICY_TYPE_MICROSERVICE and isinstance(policy_config, dict):
            return policy_config.get(POLICY_CONFIG_CONTENT)

        return policy_config

    @staticmethod
    def _store_policy_apply_order_clause(policy_apply_order_path):
        """
        Find the field :policy_apply_order_path: that is provided as an optional parameter
        to gather_policies_to_node decorator.

        Parse the field-pathes found in the :policy_apply_order_path: field.

        Store the result into :runtime_properties[POLICY_APPLY_ORDER_CLAUSE]:

        Example:
            policy_apply_order_path = "docker_config:policy:apply_order"
            will take the list of field-pathes from the field
                properties:
                    docker_config:
                        policy:
                            apply_order:
        """
        if not policy_apply_order_path:
            return

        policy_apply_order_clause = Utils.get_field_value(
            dict(ctx.node.properties),
            policy_apply_order_path
        )

        if not policy_apply_order_clause:
            ctx.logger.warn("not found policy_apply_order_path: {0} in node.properties"
                            .format(policy_apply_order_path))
            return

        ctx.instance.runtime_properties[POLICY_APPLY_ORDER_CLAUSE] = policy_apply_order_clause

    @staticmethod
    def _set_policy_apply_order(policies):
        """
        Calculates, sorts and stores the policy_apply_order for policies.

        Sorting is done based on the list of field-pathes
        specified in :runtime_properties[POLICY_APPLY_ORDER_CLAUSE]:

        The apply_order field is expected to be formatted as the list of strings.
        Each string can contain the path to the field inside the policy_body object
        with the same delimiter of ":" (semicolon).
        To convert the field to decimal, use ::number suffix after the field name.
        To specify the descending order, add "desc" after the whitespace.

        Example:
            apply_order = ["matchingConditions:priority::number desc",
                           "config:foo desc nulls-last", "config:db_client"]

        this will return the policies starting with the highest decimal value in "priority"
        field inside the "matchingConditions".
        Then the policies with the same "priority" values will be sorted in descending order
        by the string value in the field "foo" found inside the "config".
        Then the policies with the same "priority" and "foo" values will be sorted
        by the string value in the field "db_client" found inside the "config".
        Then the policies with the same "priority" and "foo" and "db_client" field values will
        further be always sorted by "policy_id" - no need to specify that in apply_order.
        Sorting by policy_id insures the uniqueness and predictability of the policy apply_order.

        An invalid field-path will result in the value of None that brings this record upfront.
        """
        policy_apply_order = [policy_id
                              for (policy_id, policy) in policies.iteritems()
                              if Policies._get_config_from_policy(policy)]

        if not policy_apply_order:
            ctx.instance.runtime_properties[POLICY_APPLY_ORDER] = policy_apply_order
            return

        policy_apply_order.sort()

        policy_apply_order_clause = ctx.instance.runtime_properties.get(POLICY_APPLY_ORDER_CLAUSE)
        if not policy_apply_order_clause:
            ctx.instance.runtime_properties[POLICY_APPLY_ORDER] = policy_apply_order
            return

        if not isinstance(policy_apply_order_clause, list):
            policy_apply_order_clause = [policy_apply_order_clause]

        for clause_item in reversed(policy_apply_order_clause):
            f_path, f_type, desc, n_last = Utils.parse_clause_item(clause_item)

            if not f_path:
                continue

            policy_apply_order.sort(
                key=lambda policy_id, fpath=f_path, ftype=f_type, reverse=desc, nulls_last=n_last:
                Utils.key_with_none_in_sort(
                    reverse, nulls_last,
                    Utils.get_field_value(
                        policies.get(policy_id, {}).get(POLICY_BODY, {}),
                        fpath,
                        field_type=ftype
                    )
                ), reverse=desc
            )

        ctx.instance.runtime_properties[POLICY_APPLY_ORDER] = policy_apply_order

    @staticmethod
    def _set_policy_defaulted_fields(policies):
        """
        Keeps track and stores the dict of field names of removed policies into
        :runtime_properties[POLICY_DEFAULTED_FIELDS]:
        """
        policy_defaulted_fields = ctx.instance.runtime_properties.get(POLICY_DEFAULTED_FIELDS, {})
        policy_defaulted_fields.update(
            (field_name, True)
            for policy in Policies._removed_policies.itervalues()
            for field_name in Policies._get_config_from_policy(policy) or {}
        )
        if policies:
            for policy in policies.itervalues():
                for field_name in Policies._get_config_from_policy(policy) or {}:
                    if field_name in policy_defaulted_fields:
                        del policy_defaulted_fields[field_name]

        ctx.instance.runtime_properties[POLICY_DEFAULTED_FIELDS] = policy_defaulted_fields

    @staticmethod
    def _set_policies(policies):
        """
        store the :policies: in :runtime_properties[POLICIES]:

        and build an index on policies into :runtime_properties[POLICY_APPLY_ORDER]:

        and keep track of fields from previously :removed: policy-configs in
            :runtime_properties[POLICY_DEFAULTED_FIELDS]: to reset them to default values
            on merging the policies into config
        """
        Policies._set_policy_defaulted_fields(policies)
        if not policies:
            if POLICIES in ctx.instance.runtime_properties:
                del ctx.instance.runtime_properties[POLICIES]
            if POLICY_APPLY_ORDER in ctx.instance.runtime_properties:
                del ctx.instance.runtime_properties[POLICY_APPLY_ORDER]
            return

        ctx.instance.runtime_properties[POLICIES] = policies
        Policies._set_policy_apply_order(policies)

    @staticmethod
    def _get_policy_bodies_dict(policies):
        """returns a dict of policy_id -> policy_body if policy_body exists"""
        if not policies:
            return {}

        return dict((policy_id, policy.get(POLICY_BODY))
            for policy_id, policy in policies.iteritems() if policy.get(POLICY_BODY)
        )

    @staticmethod
    def gather_policies_to_node(policy_apply_order_path=None):
        """
        decorate with @Policies.gather_policies_to_node() to
        gather the policies from dcae.nodes.policy nodes this node depends on.

        Places the policies into runtime_properties["policies"].

        Stores <scn>:policies data in consul-kv

        Call Policies.calc_latest_application_config() to apply policies onto application_config.
        """
        def gather_policies_decorator(func):
            """the decorator"""
            if not func:
                return

            def add_policy(policy_id, policy, policy_persistent, policies):
                """only add the latest version of policy to policies"""
                prev_policy = policies.get(policy_id)
                prev_policy_persistent = (prev_policy or {}).get(POLICY_PERSISTENT)

                if not prev_policy \
                or (policy_persistent and not prev_policy_persistent) \
                or (policy_persistent == prev_policy_persistent and policy.get(POLICY_BODY)):
                    policy = deepcopy(policy)
                    policy[POLICY_PERSISTENT] = policy_persistent
                    policies[policy_id] = policy

            def gather_policy(target, policies):
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

                add_policy(policy_id, policy, True, policies)
                return True

            def gather_policies(target, policies, policy_filters):
                """adds the policies and policy-filter from dcae.nodes.policies node to policies"""
                if DCAE_POLICIES_TYPE not in target.node.type_hierarchy:
                    return

                property_policy_filter = target.node.properties.get(POLICY_FILTER)
                if property_policy_filter:
                    policy_filter = dict(
                        (k, v) for (k, v) in dict(property_policy_filter).iteritems()
                        if v or isinstance(v, (int, float))
                    )
                    if policy_filter:
                        policy_filters[target.instance.id] = {
                            POLICY_FILTER_ID : target.instance.id,
                            POLICY_FILTER : deepcopy(policy_filter)
                        }

                filtered_policies = target.instance.runtime_properties.get(POLICIES_FILTERED)
                if not filtered_policies or not isinstance(filtered_policies, dict):
                    return True
                for (policy_id, policy) in filtered_policies.iteritems():
                    add_policy(policy_id, policy, False, policies)
                return True

            @wraps(func)
            def wrapper(*args, **kwargs):
                """gather and save the policies from dcae.nodes.policy nodes this node related to"""
                if ctx.type != NODE_INSTANCE:
                    raise NonRecoverableError("can only invoke gather_policies_to_node on node")

                policies_outputted = False
                policy_bodies = []
                try:
                    Policies._store_policy_apply_order_clause(policy_apply_order_path)

                    policies = {}
                    policy_filters = {}
                    for rel in ctx.instance.relationships:
                        _ = gather_policy(rel.target, policies) \
                         or gather_policies(rel.target, policies, policy_filters)

                    Policies._set_policies(policies)
                    if policy_filters:
                        ctx.instance.runtime_properties[POLICY_FILTERS] = policy_filters

                    policy_bodies = Policies._get_policy_bodies_dict(policies)
                    if policy_bodies:
                        policies_outputted = PoliciesOutput.store_policies(ACTION_GATHERED, policy_bodies)
                except Exception as ex:
                    error = "Failed to set the policies {0}".format(str(ex))
                    ctx.logger.error("{0}: {1}".format(error, traceback.format_exc()))
                    raise NonRecoverableError(error)

                func_result = func(*args, **kwargs)

                if not policies_outputted and policy_bodies:
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
            ctx.logger.error(
                "update_policies_on_ctx - no updated, added, or removed policies received")
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
                                                                     .get(POLICIES, {}).iteritems())

        ctx.logger.info("new_policies: {0}".format(json.dumps(new_policies)))

        for (policy_id, policy) in new_policies.iteritems():
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
    def update_policies_on_node(configs_only=False):
        """
        decorate each policy_update operation with @Policies.update_policies_on_node to
        filter out the updated_policies to only what applies to the current node instance,
        update runtime_properties["policies"]

        updates <scn>:policies data in consul-kv

        :configs_only: - set to True if expect to see only the config in updated_policies
            instead of the whole policy_body object (False)

        Passes through the filtered list of updated_policies that apply to the current node instance

        :updated_policies: contains the list of changed policy-configs when configs_only=True.
        """
        def update_policies_decorator(func):
            """actual decorator"""
            if not func:
                return

            @wraps(func)
            def wrapper(updated_policies=None,
                        added_policies=None,
                        removed_policies=None,
                        **kwargs):
                """update matching policies on the node"""
                if ctx.type != NODE_INSTANCE:
                    raise NonRecoverableError("can only invoke update_policies_on_node on node")

                try:
                    Policies._update_policies(updated_policies, added_policies, removed_policies)

                    updated_policies = deepcopy(Policies._get_ordered_policies(
                        selected_policies=Policies._updated_policies
                    ))
                    removed_policies = deepcopy(Policies._removed_policies.values())

                    if configs_only:
                        updated_policies = Utils.remove_empties(
                            [Policies._get_config_from_policy(policy)
                             for policy in updated_policies]
                        )
                        removed_policies = [Policies._get_config_from_policy(policy)
                                            for policy in removed_policies]
                    else:
                        updated_policies = Utils.remove_empties(
                            [policy.get(POLICY_BODY) for policy in updated_policies]
                        )
                        removed_policies = [policy.get(POLICY_BODY)
                                            for policy in removed_policies]

                except Exception as ex:
                    error = "Failed to update the policies {0}".format(str(ex))
                    ctx.logger.error("{0}: {1}".format(error, traceback.format_exc()))
                    raise NonRecoverableError(error)

                if updated_policies or removed_policies:
                    return func(
                        updated_policies,
                        removed_policies=removed_policies,
                        policies=Policies.get_policy_bodies(),
                        **kwargs)
            return wrapper
        return update_policies_decorator

    @staticmethod
    def cleanup_policies_on_node(func):
        """
        decorate each policy_update operation with @Policies.cleanup_policies_on_node to
        remove <scn>:policies data in consul-kv
        """
        if not func:
            return

        @wraps(func)
        def wrapper(**kwargs):
            """cleanup policies in consul-kv"""
            if ctx.type != NODE_INSTANCE:
                raise NonRecoverableError("can only invoke cleanup_policies_on_node on node")

            try:
                PoliciesOutput.delete_policies()
            except Exception as ex:
                error = "Failed to cleanup policies in consul-kv {0}".format(str(ex))
                ctx.logger.error("{0}: {1}".format(error, traceback.format_exc()))

            return func(**kwargs)
        return wrapper

    @staticmethod
    def _get_ordered_policies(selected_policies=None):
        """returns the ordered list of selected policies from the runtime policies"""
        policies = ctx.instance.runtime_properties.get(POLICIES)
        apply_order = ctx.instance.runtime_properties.get(POLICY_APPLY_ORDER)
        if not policies or not apply_order:
            return []

        if selected_policies is None:
            return [policies[policy_id] for policy_id in apply_order]

        if not selected_policies:
            return []

        return [policies[policy_id] for policy_id in apply_order if policy_id in selected_policies]

    @staticmethod
    def get_policy_configs():
        """returns the ordered list of policy configs from the runtime policies"""
        if ctx.type != NODE_INSTANCE:
            return []

        ordered_policies = Policies._get_ordered_policies()
        return Utils.remove_empties(
            [Policies._get_config_from_policy(policy)
             for policy in ordered_policies]
        )

    @staticmethod
    def get_policy_bodies():
        """returns the ordered list of policy_body objects if policy_body exists"""
        return [policy.get(POLICY_BODY)
                for policy in Policies._get_ordered_policies()
                if policy.get(POLICY_BODY)]

    @staticmethod
    def shallow_merge_policies_into(config, default_config=None):
        """
        shallow merge the :policy configs: (dict) into :config: that is expected to be a dict.

        the fields listed in :runtime_properties[POLICY_DEFAULTED_FIELDS]:
        that where ever changed by policy-configs are initially reset to default values
        found in :default_config: or :node.properties[APPLICATION_CONFIG]:
            on merging the policies into config
        """
        if config is None:
            config = {}

        policy_configs = Policies.get_policy_configs()

        if not config or not isinstance(config, dict):
            ctx.logger.warn("unexpected config {0} to merge the policy_configs {1} into" \
                .format(json.dumps(config), json.dumps(policy_configs or [])))
            return config

        defaulted_fields = ctx.instance.runtime_properties.get(POLICY_DEFAULTED_FIELDS)
        if defaulted_fields:
            if default_config is None or not isinstance(default_config, dict):
                default_config = dict(ctx.node.properties.get(APPLICATION_CONFIG, {}))
                ctx.logger.info("using default_config from node.properties[{0}]: {1}"
                                .format(APPLICATION_CONFIG, json.dumps(default_config)))
            if default_config and isinstance(default_config, dict):
                for defaulted_field in defaulted_fields:
                    if defaulted_field in default_config and defaulted_field in config:
                        config[defaulted_field] = deepcopy(default_config.get(defaulted_field))

                ctx.logger.info("inited config {0} on {1} {2} from {3}"
                                .format(json.dumps(config),
                                        POLICY_DEFAULTED_FIELDS,
                                        json.dumps(defaulted_fields),
                                        json.dumps(default_config)))

        if not policy_configs:
            ctx.logger.warn("no policies to merge to config {0}".format(json.dumps(config)))
            return config

        for policy_config in policy_configs:
            if not isinstance(policy_config, dict):
                ctx.logger.warn("skipped unexpected format of policy_config {0} for config: {1}" \
                    .format(json.dumps(policy_config), json.dumps(config)))
                continue

            ctx.logger.info("applying policy_config {0} to config {1}" \
                .format(json.dumps(policy_config), json.dumps(config)))
            for (policy_key, policy_value) in policy_config.iteritems():
                if policy_key not in config or policy_value is None:
                    ctx.logger.warn("skipped unexpected policy({0}, {1}) for config: {2}" \
                        .format(policy_key, json.dumps(policy_value), json.dumps(config)))
                    continue
                config[policy_key] = deepcopy(policy_value)

        return config

    @staticmethod
    def calc_latest_application_config(application_config_name=None):
        """
        shallow merge the policy configs (dict) into config that is expected to be a dict

        if :application_config_name: is not provided,
        the runtime property :application_config: on the node instance is used as initial config
        """
        if not application_config_name:
            application_config_name = APPLICATION_CONFIG

        config = deepcopy(dict(ctx.instance.runtime_properties.get(application_config_name, {})))
        if not config:
            config = deepcopy(dict(ctx.node.properties.get(application_config_name, {})))

        ctx.logger.info("going to merge policies over {0}: {1}" \
            .format(application_config_name, json.dumps(config)))

        return Policies.shallow_merge_policies_into(config)
