# ============LICENSE_START=======================================================
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

"""tests of decorators around the cloudify operations to handle policy actions"""

import copy
import json
import logging
from datetime import datetime, timedelta
from functools import wraps

import pytest
import requests
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
from cloudify.state import current_ctx

from onap_dcae_dcaepolicy_lib import dcae_policy
from onap_dcae_dcaepolicy_lib.dcae_policy import Policies
from onap_dcae_dcaepolicy_lib.policies_output import PoliciesOutput
from tests.log_ctx import CtxLogger
from tests.mock_cloudify_ctx import (TARGET_NODE_ID, TARGET_NODE_NAME,
                                     MockCloudifyContextFull)

POLICY_ID = 'policy_id'
POLICY_VERSION = "policyVersion"
POLICY_NAME = "policyName"
POLICY_BODY = 'policy_body'
POLICY_CONFIG = 'config'
CONFIG_NAME = "ConfigName"

MONKEYED_POLICY_ID = 'monkeyed.Config_peach'
MONKEYED_POLICY_ID_2 = 'monkeyed.Config_peach_2'
MONKEYED_POLICY_ID_M = 'monkeyed.Config_multi'
MONKEYED_POLICY_ID_M_2 = 'monkeyed.Config_multi_2'
MONKEYED_POLICY_ID_M_3 = 'monkeyed.Config_multi_3'
MONKEYED_POLICY_ID_B = 'monkeyed.Config_both'
APPLICATION_CONFIG = "application_config"
LOG_FILE = 'logs/test_onap_dcae_dcaepolicy_lib.log'
LOREM_IPSUM = """Lorem ipsum dolor sit amet consectetur ametist""".split()

RUN_TS = datetime.utcnow()

class MonkeyedLogHandler(object):
    """keep the shared logger handler here"""
    _log_handler = None

    @staticmethod
    def add_handler_to(logger):
        """adds the local handler to the logger"""
        if not MonkeyedLogHandler._log_handler:
            MonkeyedLogHandler._log_handler = logging.FileHandler(LOG_FILE)
            MonkeyedLogHandler._log_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                fmt='%(asctime)s.%(msecs)03d %(levelname)+8s ' + \
                    '%(threadName)s %(name)s.%(funcName)s: %(message)s', \
                datefmt='%Y%m%d_%H%M%S')
            MonkeyedLogHandler._log_handler.setFormatter(formatter)
        logger.addHandler(MonkeyedLogHandler._log_handler)

class MonkeyedPolicyBody(object):
    """policy body that policy-engine returns"""
    @staticmethod
    def create_policy_body(policy_id, policy_version=1, priority=None, **kwargs):
        """returns a fake policy-body"""
        prev_ver = policy_version - 1
        timestamp = RUN_TS + timedelta(hours=prev_ver)

        this_ver = str(policy_version)
        config = {
            "policy_updated_from_ver": str(prev_ver),
            "policy_updated_to_ver": this_ver,
            "policy_hello": LOREM_IPSUM[prev_ver % len(LOREM_IPSUM)],
            "policy_updated_ts": timestamp.isoformat()[:-3] + 'Z',
            "updated_policy_id": policy_id
        }
        config.update(copy.deepcopy(kwargs) or {})

        matching_conditions = {
            "ONAPName": "DCAE",
            CONFIG_NAME: "alex_config_name"
        }
        if priority is not None:
            matching_conditions["priority"] = priority

        return {
            "policyConfigMessage": "Config Retrieved! ",
            "policyConfigStatus": "CONFIG_RETRIEVED",
            "type": "JSON",
            POLICY_NAME: "{0}.{1}.xml".format(policy_id, this_ver),
            POLICY_VERSION: this_ver,
            POLICY_CONFIG: config,
            "matchingConditions": matching_conditions,
            "responseAttributes": {},
            "property": None
        }

    @staticmethod
    def create_policy_bare(policy_id, policy_version=1, priority=None, **kwargs):
        """returns the whole policy object for policy_id and policy_version"""
        return {
            POLICY_ID: policy_id,
            POLICY_BODY: MonkeyedPolicyBody.create_policy_body(
                policy_id, policy_version, priority, **kwargs)
        }

    @staticmethod
    def create_policy(policy_id, policy_version=1, policy_persistent=True, priority=None, **kwargs):
        """returns the whole policy object for policy_id and policy_version"""
        policy = MonkeyedPolicyBody.create_policy_bare(
            policy_id, policy_version, priority, **kwargs)
        policy[dcae_policy.POLICY_PERSISTENT] = bool(policy_persistent)
        return policy

    @staticmethod
    def is_the_same_dict(policy_body_1, policy_body_2):
        """check whether both policy_body objects are the same"""
        if not isinstance(policy_body_1, dict) or not isinstance(policy_body_2, dict):
            return False
        for key in policy_body_1:
            if key not in policy_body_2:
                return False

            val_1 = policy_body_1[key]
            val_2 = policy_body_2[key]
            if (val_1 is None) != (val_2 is None):
                return False
            if isinstance(val_1, dict) \
            and not MonkeyedPolicyBody.is_the_same_dict(val_1, val_2):
                return False
            if val_1 != val_2:
                return False
        return True

class MonkeyedNode(object):
    """node in cloudify"""
    BLUEPRINT_ID = 'test_dcae_policy_bp_id'
    DEPLOYMENT_ID = 'test_dcae_policy_dpl_id'
    EXECUTION_ID = 'test_dcae_policy_exe_id'

    def __init__(self, node_id, node_name, node_type, properties=None,
                 relationships=None, runtime_properties=None):
        self.node_id = node_id
        self.node_name = node_name
        self.ctx = MockCloudifyContextFull(
            node_id=self.node_id,
            node_name=self.node_name,
            node_type=node_type,
            blueprint_id=MonkeyedNode.BLUEPRINT_ID,
            deployment_id=MonkeyedNode.DEPLOYMENT_ID,
            execution_id=MonkeyedNode.EXECUTION_ID,
            properties=properties,
            relationships=relationships,
            runtime_properties=runtime_properties
        )

class MonkeyedResponse(object):
    """Monkey response"""
    def __init__(self, full_path, headers=None, resp_json=None):
        self.full_path = full_path
        self.status_code = 200
        self.headers = headers or {}
        self.resp_json = resp_json
        self.text = json.dumps(resp_json or {})

    def json(self):
        """returns json of response"""
        return self.resp_json

    def raise_for_status(self):
        """always happy"""
        pass

def get_app_config():
    """just get the config"""
    config = copy.deepcopy(dict(ctx.instance.runtime_properties.get(APPLICATION_CONFIG, {})))
    if not config:
        config = copy.deepcopy(dict(ctx.node.properties.get(APPLICATION_CONFIG, {})))
    return config

def operation_node_configure(**kwargs):
    """do the node-configure operation"""
    ctx.logger.info("operation_node_configure kwargs: {0}".format(kwargs))

    app_config = get_app_config()
    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config
    ctx.instance.runtime_properties[PoliciesOutput.SERVICE_COMPONENT_NAME] = "unit_test_scn"
    ctx.logger.info("property app_config: {0}".format(json.dumps(app_config)))

@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='exe_task')
@Policies.gather_policies_to_node()
def node_configure(**kwargs):
    """decorate with @Policies.gather_policies_to_node on policy consumer node to
    bring all policies to runtime_properties["policies"]
    """
    operation_node_configure(**kwargs)

@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='execute_operation')
@Policies.update_policies_on_node()
def policy_update(updated_policies, removed_policies=None, **kwargs):
    """decorate with @Policies.update_policies_on_node() to update runtime_properties["policies"]

    :updated_policies: contains the list of changed policy-configs when configs_only=True (default).
    """
    # This is how to merge the policies into default app_config object
    #               (runtime_properties[APPLICATION_CONFIG] = application_config)
    app_config = get_app_config()
    ctx.logger.info("app_config {0}".format(json.dumps(app_config)))

    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config

@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='execute_operation')
@Policies.update_policies_on_node()
def policy_update_not_only_config(updated_policies, removed_policies=None, **kwargs):
    """decorate with @Policies.update_policies_on_node() to update runtime_properties["policies"]

    :updated_policies: contains the list of changed policy-configs when configs_only=True (default).
    """
    # This is how to merge the policies into default app_config object
    #               (runtime_properties[APPLICATION_CONFIG] = application_config)
    app_config = get_app_config()
    ctx.logger.info("app_config {0}".format(json.dumps(app_config)))

    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config

@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='execute_operation')
@Policies.update_policies_on_node()
def policy_update_many_calcs(updated_policies, removed_policies=None, policies=None, **kwargs):
    """decorate with @Policies.update_policies_on_node() to update runtime_properties["policies"]

    :updated_policies: contains the list of changed policy-configs when configs_only=True (default).
    """
    app_config = get_app_config()
    ctx.logger.info("app_config {0}".format(json.dumps(app_config)))

    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config


@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='exe_task')
@Policies.cleanup_policies_on_node
def node_delete(**kwargs):
    """delete <service_component_name> records in consul-kv"""
    operation_node_configure(**kwargs)


class CurrentCtx(object):
    """cloudify context"""
    _node_ms = None

    @staticmethod
    def set_current_ctx(include_bad=True, include_good=True):
        """set up the nodes for cloudify"""
        Policies._init()

        def add_target_to_relationships(relationships, node):
            """adds the node as the target of relationships"""
            relationships.append({TARGET_NODE_ID: node.node_id, TARGET_NODE_NAME: node.node_name})

        relationships = []
        if include_good:
            node_policy = MonkeyedNode(
                'dcae_policy_node_id',
                'dcae_policy_node_name',
                dcae_policy.DCAE_POLICY_TYPE,
                {POLICY_ID: MONKEYED_POLICY_ID},
                None,
                {POLICY_BODY: MonkeyedPolicyBody.create_policy_body(
                    MONKEYED_POLICY_ID, priority="1")}
            )
            add_target_to_relationships(relationships, node_policy)

        if include_bad:
            bad_policy_2 = MonkeyedNode(
                'bad_policy_2_node_id',
                'bad_policy_2_node_name',
                dcae_policy.DCAE_POLICY_TYPE,
                {POLICY_ID: MONKEYED_POLICY_ID_2},
                None,
                None
            )
            add_target_to_relationships(relationships, bad_policy_2)

        if include_good:
            node_policy_2 = MonkeyedNode(
                'dcae_policy_node_id_2',
                'dcae_policy_node_name_2',
                dcae_policy.DCAE_POLICY_TYPE,
                {POLICY_ID: MONKEYED_POLICY_ID_2},
                None,
                {POLICY_BODY: MonkeyedPolicyBody.create_policy_body(
                    MONKEYED_POLICY_ID_2, 4, priority="2")}
            )
            add_target_to_relationships(relationships, node_policy_2)

        if include_bad:
            bad_policy_3 = MonkeyedNode(
                'bad_policy_3_node_id',
                'bad_policy_3_node_name',
                dcae_policy.DCAE_POLICY_TYPE,
                {POLICY_ID: MONKEYED_POLICY_ID_2},
                None,
                None
            )
            add_target_to_relationships(relationships, bad_policy_3)

            bad_policy_4 = MonkeyedNode(
                'bad_policy_4_node_id',
                'bad_policy_4_node_name',
                dcae_policy.DCAE_POLICY_TYPE,
                None,
                None,
                None
            )
            add_target_to_relationships(relationships, bad_policy_4)

            weird_policy_5 = MonkeyedNode(
                'weird_policy_5_node_id',
                'weird_policy_5_node_name',
                dcae_policy.DCAE_POLICY_TYPE,
                None,
                None,
                {POLICY_BODY: MonkeyedPolicyBody.create_policy_body(
                    MONKEYED_POLICY_ID, 3, priority="2")}
            )
            add_target_to_relationships(relationships, weird_policy_5)

        if include_good:
            node_policies = MonkeyedNode(
                'dcae_policies_node_id',
                'dcae_policies_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                {dcae_policy.POLICY_FILTER: {
                    POLICY_NAME: MONKEYED_POLICY_ID_M + ".*",
                    dcae_policy.CONFIG_ATTRIBUTES: json.dumps({
                        CONFIG_NAME: "alex_config_name"
                    })
                }},
                None,
                {dcae_policy.POLICIES_FILTERED: {
                    MONKEYED_POLICY_ID_M:
                        MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_M, 3)}}
            )
            add_target_to_relationships(relationships, node_policies)

            node_policies_2 = MonkeyedNode(
                'dcae_policies_2_node_id',
                'dcae_policies_2_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                {dcae_policy.POLICY_FILTER: {POLICY_NAME: MONKEYED_POLICY_ID_M + ".*"}},
                None,
                {dcae_policy.POLICIES_FILTERED: {
                    MONKEYED_POLICY_ID_M:
                        MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_M, 2)}}
            )
            add_target_to_relationships(relationships, node_policies_2)

            policies_empty = MonkeyedNode(
                'dcae_policies_empty_node_id',
                'dcae_policies_empty_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                {dcae_policy.POLICY_FILTER: {"empty": None}},
                None,
                None
            )
            add_target_to_relationships(relationships, policies_empty)

            policies_empty_2 = MonkeyedNode(
                'dcae_policies_empty_2_node_id',
                'dcae_policies_empty_2_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                None,
                None,
                None
            )
            add_target_to_relationships(relationships, policies_empty_2)

        non_policies = MonkeyedNode(
            'non_policies_node_id',
            'non_policies_node_name',
            "non.policy.type"
        )
        add_target_to_relationships(relationships, non_policies)

        if include_good:
            node_policies_b = MonkeyedNode(
                'dcae_policies_b_node_id',
                'dcae_policies_b_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                {dcae_policy.POLICY_FILTER: {POLICY_NAME: MONKEYED_POLICY_ID_M + ".*"}},
                None,
                {dcae_policy.POLICIES_FILTERED: {
                    MONKEYED_POLICY_ID_B:
                        MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_B, 1)}}
            )
            add_target_to_relationships(relationships, node_policies_b)

            node_policies_b_2 = MonkeyedNode(
                'dcae_policies_b_2_node_id',
                'dcae_policies_b_2_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                {dcae_policy.POLICY_FILTER: {POLICY_NAME: MONKEYED_POLICY_ID_M + ".*"}},
                None,
                {dcae_policy.POLICIES_FILTERED: {
                    MONKEYED_POLICY_ID_B:
                        MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_B, 2)}}
            )
            add_target_to_relationships(relationships, node_policies_b_2)

        if include_good:
            node_policy_b = MonkeyedNode(
                'dcae_policy_b_node_id',
                'dcae_policy_b_node_name',
                dcae_policy.DCAE_POLICY_TYPE,
                {POLICY_ID: MONKEYED_POLICY_ID_B},
                None,
                {POLICY_BODY: MonkeyedPolicyBody.create_policy_body(
                    MONKEYED_POLICY_ID_B, 4, priority="1.5")}
            )
            add_target_to_relationships(relationships, node_policy_b)

            node_policies_b_5 = MonkeyedNode(
                'dcae_policies_b_5_node_id',
                'dcae_policies_b_5_node_name',
                dcae_policy.DCAE_POLICIES_TYPE,
                {dcae_policy.POLICY_FILTER: {POLICY_NAME: MONKEYED_POLICY_ID_M + ".*"}},
                None,
                {dcae_policy.POLICIES_FILTERED: {
                    MONKEYED_POLICY_ID_B:
                        MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_B, 5)}}
            )
            add_target_to_relationships(relationships, node_policies_b_5)


        CurrentCtx._node_ms = MonkeyedNode(
            'test_ms_id', 'test_ms_name', "ms.nodes.type",
            {APPLICATION_CONFIG: MonkeyedPolicyBody.create_policy_body(
                 "no_policy", db_port="123", weather="snow")[POLICY_CONFIG]
            },
            relationships
        )
        current_ctx.set(CurrentCtx._node_ms.ctx)
        MonkeyedLogHandler.add_handler_to(CurrentCtx._node_ms.ctx.logger)

    @staticmethod
    def reset():
        """reset context"""
        current_ctx.set(CurrentCtx._node_ms.ctx)


def monkeyed_consul_boom(full_path, json):
    """boom on monkeypatch for the put to consul"""
    raise requests.ConnectionError("monkey-boom")


@pytest.fixture()
def fix_consul_boom(monkeypatch):
    """monkeyed discovery request.put"""
    PoliciesOutput._lazy_inited = False
    monkeypatch.setattr('requests.put', monkeyed_consul_boom)
    yield fix_consul_boom
    PoliciesOutput._lazy_inited = False


def monkeyed_consul_put(full_path, json):
    """monkeypatch for the put to consul"""
    return MonkeyedResponse(full_path)


@pytest.fixture()
def fix_consul(monkeypatch):
    """monkeyed discovery request.put"""
    PoliciesOutput._lazy_inited = False
    monkeypatch.setattr('requests.put', monkeyed_consul_put)
    yield fix_consul
    PoliciesOutput._lazy_inited = False


def cfy_ctx(include_bad=True, include_good=True):
    """test and safely clean up"""
    def cfy_ctx_decorator(func):
        """test and safely clean up"""
        if not func:
            return

        @wraps(func)
        def ctx_wrapper(*args, **kwargs):
            """test"""
            try:
                CurrentCtx.set_current_ctx(include_bad, include_good)

                func(*args, **kwargs)

            finally:
                ctx.logger.info("MockCloudifyContextFull.clear")
                MockCloudifyContextFull.clear()
                current_ctx.clear()

        return ctx_wrapper
    return cfy_ctx_decorator

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_gather_policies_to_node():
    """test gather_policies_to_node"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_policies_to_node():
    """test gather_policies_to_node"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    assert MONKEYED_POLICY_ID in policies
    expected_1 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID, priority="1")
    policy = policies[MONKEYED_POLICY_ID]
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

    assert MONKEYED_POLICY_ID_B in policies
    expected_b = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_B, 4, priority="1.5")
    policy = policies[MONKEYED_POLICY_ID_B]
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(expected_b)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_b)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_b, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    expected_2 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 4, priority="2")
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(expected_2)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_2)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_2, policy)

    assert MONKEYED_POLICY_ID_M in policies
    expected_m = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M, 2, False)
    policy = policies[MONKEYED_POLICY_ID_M]
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_M, json.dumps(expected_m)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_m)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_m, policy)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_update_policies():
    """test policy_update"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    updated_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2, priority="aa20")
    added_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M_2, 2,
                                                    False, priority="1")
    ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

    ctx.logger.info("policy[{0}]: not yet in policies".format(MONKEYED_POLICY_ID_M_2))
    assert MONKEYED_POLICY_ID_M_2 not in policies

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update(updated_policies=[updated_policy],
                  added_policies={
                      policy_filter_ids[0]: {
                          dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}}
                  },
                  removed_policies=[MONKEYED_POLICY_ID_M])

    ctx.logger.info("policy[{0}]: removed".format(MONKEYED_POLICY_ID_M))
    assert MONKEYED_POLICY_ID_M not in policies

    assert MONKEYED_POLICY_ID_M_2 in policies
    policy = policies[MONKEYED_POLICY_ID_M_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, added_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(added_policy, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, updated_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(updated_policy, policy)

    assert MONKEYED_POLICY_ID in policies
    policy = policies[MONKEYED_POLICY_ID]
    expected_1 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID, priority="1")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

    assert MONKEYED_POLICY_ID_B in policies
    policy = policies[MONKEYED_POLICY_ID_B]
    expected_b = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_B, 4, priority="1.5")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_b)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_b, policy)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_update_not_only_config():
    """test policy_update"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    updated_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2, priority="aa20")
    added_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M_2, 2,
                                                    False, priority="1")
    ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

    ctx.logger.info("policy[{0}]: not yet in policies".format(MONKEYED_POLICY_ID_M_2))
    assert MONKEYED_POLICY_ID_M_2 not in policies

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update_not_only_config(updated_policies=[updated_policy],
                                  added_policies={
                                      policy_filter_ids[0]: {
                                          dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}}
                                  },
                                  removed_policies=[MONKEYED_POLICY_ID_M])

    ctx.logger.info("policy[{0}]: removed".format(MONKEYED_POLICY_ID_M))
    assert MONKEYED_POLICY_ID_M not in policies

    assert MONKEYED_POLICY_ID_M_2 in policies
    policy = policies[MONKEYED_POLICY_ID_M_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, added_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(added_policy, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, updated_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(updated_policy, policy)

    assert MONKEYED_POLICY_ID in policies
    policy = policies[MONKEYED_POLICY_ID]
    expected_1 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID, priority="1")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

    assert MONKEYED_POLICY_ID_B in policies
    policy = policies[MONKEYED_POLICY_ID_B]
    expected_b = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_B, 4, priority="1.5")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_b)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_b, policy)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_update_policies_not():
    """test policy_update - ignore all policies with junk params"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    assert APPLICATION_CONFIG in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    app_config = runtime_properties[APPLICATION_CONFIG]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))
    ctx.logger.info("app_config: {0}".format(json.dumps(app_config)))

    expected_policies = copy.deepcopy(policies)
    expected_app_config = copy.deepcopy(app_config)

    existing_policy = MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID, priority="1")
    damaged_policy = MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_2)
    del damaged_policy[POLICY_BODY][POLICY_CONFIG]
    updated_policy = MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_M_3, 3)
    added_policy = MonkeyedPolicyBody.create_policy_bare(MONKEYED_POLICY_ID_M_2, 4)
    junk_policy_filter_id = "<<<junk_removed_policy_id>>>"
    unexpected_removed_policy_id = "<<<junk_removed_policy_id>>>"
    ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

    assert MONKEYED_POLICY_ID in policies
    assert MONKEYED_POLICY_ID_2 in policies
    assert MONKEYED_POLICY_ID_M_2 not in policies
    assert MONKEYED_POLICY_ID_M_3 not in policies
    assert unexpected_removed_policy_id not in policies
    assert junk_policy_filter_id not in runtime_properties.get(dcae_policy.POLICY_FILTERS, {})

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update(updated_policies=[existing_policy, damaged_policy, updated_policy],
                  added_policies={
                      junk_policy_filter_id: {
                          dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}},
                      policy_filter_ids[0]: {
                          dcae_policy.POLICIES: {MONKEYED_POLICY_ID_2: damaged_policy}}
                  },
                  removed_policies=[unexpected_removed_policy_id])

    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    ctx.logger.info("policies not changed: {0}".format(json.dumps(policies)))
    assert MonkeyedPolicyBody.is_the_same_dict(policies, expected_policies)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_policies, policies)

    ctx.logger.info("app_config not changed: {0}".format(json.dumps(app_config)))
    assert MonkeyedPolicyBody.is_the_same_dict(app_config, expected_app_config)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_app_config, app_config)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_update_many_calcs():
    """test policy_update"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    updated_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2, priority="aa20")
    added_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M_2, 2,
                                                    False, priority="1")
    ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

    ctx.logger.info("policy[{0}]: not yet in policies".format(MONKEYED_POLICY_ID_M_2))
    assert MONKEYED_POLICY_ID_M_2 not in policies

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update_many_calcs(updated_policies=[updated_policy],
                             added_policies={
                                 policy_filter_ids[0]: {
                                     dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}}
                             },
                             removed_policies=[MONKEYED_POLICY_ID_M])

    ctx.logger.info("policy[{0}]: removed".format(MONKEYED_POLICY_ID_M))
    assert MONKEYED_POLICY_ID_M not in policies

    assert MONKEYED_POLICY_ID_M_2 in policies
    policy = policies[MONKEYED_POLICY_ID_M_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, added_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(added_policy, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, updated_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(updated_policy, policy)

    assert MONKEYED_POLICY_ID in policies
    policy = policies[MONKEYED_POLICY_ID]
    expected_1 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID, priority="1")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

    assert MONKEYED_POLICY_ID_B in policies
    policy = policies[MONKEYED_POLICY_ID_B]
    expected_b = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_B, 4, priority="1.5")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_b)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_b, policy)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_remove_all_policies():
    """test policy_update - remove all policies"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    remove_policy_ids = list(policies)

    policy_update(updated_policies=None, added_policies=None, removed_policies=remove_policy_ids)

    ctx.logger.info("removed: {0}".format(remove_policy_ids))
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))
    assert dcae_policy.POLICIES in runtime_properties
    assert Policies.get_policy_bodies() == []

    assert APPLICATION_CONFIG in runtime_properties
    assert APPLICATION_CONFIG in ctx.node.properties
    app_config = runtime_properties[APPLICATION_CONFIG]
    expected_config = dict(ctx.node.properties[APPLICATION_CONFIG])
    ctx.logger.info("expected = default application_config: {0}".format(json.dumps(app_config)))
    assert MonkeyedPolicyBody.is_the_same_dict(app_config, expected_config)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_config, app_config)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_remove_all_policies_twice():
    """test policy_update - remove all policies twice"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    remove_policy_ids = list(policies)

    policy_update(updated_policies=None, added_policies=None, removed_policies=remove_policy_ids)
    policy_update(updated_policies=None, added_policies=None, removed_policies=remove_policy_ids)

    ctx.logger.info("removed: {0}".format(remove_policy_ids))
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))
    assert dcae_policy.POLICIES in runtime_properties
    assert Policies.get_policy_bodies() == []

    assert APPLICATION_CONFIG in runtime_properties
    assert APPLICATION_CONFIG in ctx.node.properties
    app_config = runtime_properties[APPLICATION_CONFIG]
    expected_config = dict(ctx.node.properties[APPLICATION_CONFIG])
    ctx.logger.info("expected = default application_config: {0}".format(json.dumps(app_config)))
    assert MonkeyedPolicyBody.is_the_same_dict(app_config, expected_config)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_config, app_config)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_remove_then_update():
    """test policy_update"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    remove_policy_ids = list(policies)
    policy_update(updated_policies=None, added_policies=None, removed_policies=remove_policy_ids)

    updated_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2, priority="aa20")
    added_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M_2, 2,
                                                    False, priority="1")
    ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

    ctx.logger.info("policy[{0}]: not yet in policies".format(MONKEYED_POLICY_ID_M_2))
    assert MONKEYED_POLICY_ID_M_2 not in policies

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update(updated_policies=[updated_policy],
                  added_policies={
                      policy_filter_ids[0]: {
                          dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}}
                  },
                  removed_policies=[MONKEYED_POLICY_ID_M])

    ctx.logger.info("policy[{0}]: removed".format(MONKEYED_POLICY_ID_M))
    assert MONKEYED_POLICY_ID_M not in policies

    assert MONKEYED_POLICY_ID_M_2 in policies
    policy = policies[MONKEYED_POLICY_ID_M_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, added_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(added_policy, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, updated_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(updated_policy, policy)

    assert MONKEYED_POLICY_ID in policies
    assert MONKEYED_POLICY_ID_B in policies

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_remove_update_many_calcs():
    """test policy_update"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    remove_policy_ids = list(policies)
    policy_update_many_calcs(updated_policies=None,
                             added_policies=None,
                             removed_policies=remove_policy_ids)

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    updated_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2, priority="aa20")
    added_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M_2, 2,
                                                    False, priority="1")
    ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

    ctx.logger.info("policy[{0}]: not yet in policies".format(MONKEYED_POLICY_ID_M_2))
    assert MONKEYED_POLICY_ID_M_2 not in policies

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update_many_calcs(updated_policies=[updated_policy],
                             added_policies={
                                 policy_filter_ids[0]: {
                                     dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}}
                             },
                             removed_policies=[MONKEYED_POLICY_ID_M])

    ctx.logger.info("policy[{0}]: removed".format(MONKEYED_POLICY_ID_M))
    assert MONKEYED_POLICY_ID_M not in policies

    assert MONKEYED_POLICY_ID_M_2 in policies
    policy = policies[MONKEYED_POLICY_ID_M_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, added_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(added_policy, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, updated_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(updated_policy, policy)

    assert MONKEYED_POLICY_ID in policies
    assert MONKEYED_POLICY_ID_B in policies

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_bad_update_many_calcs():
    """test policy_update"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    damaged_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2, priority="aa20")
    damaged_policy[POLICY_BODY][POLICY_CONFIG] = ["damaged config"]

    added_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_M_2, 2,
                                                    False, priority="1")
    added_policy[POLICY_BODY][POLICY_CONFIG] = {"unexpected":"foo", "none": None}

    ctx.logger.info("policy_update: [{0}]".format(json.dumps(damaged_policy)))

    ctx.logger.info("policy[{0}]: not yet in policies".format(MONKEYED_POLICY_ID_M_2))
    assert MONKEYED_POLICY_ID_M_2 not in policies

    policy_filter_ids = list(runtime_properties.get(dcae_policy.POLICY_FILTERS) or ["--"])

    policy_update_many_calcs(updated_policies=[damaged_policy],
                             added_policies={
                                 policy_filter_ids[0]: {
                                     dcae_policy.POLICIES: {MONKEYED_POLICY_ID_M_2: added_policy}}
                             },
                             removed_policies=[MONKEYED_POLICY_ID_M])

    ctx.logger.info("policy[{0}]: removed".format(MONKEYED_POLICY_ID_M))
    assert MONKEYED_POLICY_ID_M not in policies

    assert MONKEYED_POLICY_ID_M_2 in policies
    policy = policies[MONKEYED_POLICY_ID_M_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_M_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, added_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(added_policy, policy)

    assert MONKEYED_POLICY_ID_2 in policies
    policy = policies[MONKEYED_POLICY_ID_2]
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, damaged_policy)
    assert MonkeyedPolicyBody.is_the_same_dict(damaged_policy, policy)

    assert MONKEYED_POLICY_ID in policies
    policy = policies[MONKEYED_POLICY_ID]
    expected_1 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID, priority="1")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

    assert MONKEYED_POLICY_ID_B in policies
    policy = policies[MONKEYED_POLICY_ID_B]
    expected_b = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_B, 4, priority="1.5")
    ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(expected_1)))
    ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_B, json.dumps(policy)))
    assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_b)
    assert MonkeyedPolicyBody.is_the_same_dict(expected_b, policy)

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True, include_good=False)
def test_bad_policies():
    """test bad policy nodes"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True, include_good=False)
def test_wrong_ctx_node_configure():
    """test wrong ctx"""
    current_ctx.set(ctx.instance.relationships[0])
    ctx_type = ctx.type

    with pytest.raises(NonRecoverableError) as excinfo:
        node_configure()

    CurrentCtx.reset()
    ctx.logger.info("{0} not a node boom: {1}".format(ctx_type, str(excinfo.value)))
    assert ctx_type == 'cloudify.relationships.depends_on'
    assert str(excinfo.value) == "can only invoke gather_policies_to_node on node"

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True, include_good=False)
def test_wrong_ctx_policy_update():
    """test wrong ctx"""
    no_policies = Policies.get_policy_bodies()
    current_ctx.set(ctx.instance.relationships[0])
    ctx_type = ctx.type

    with pytest.raises(NonRecoverableError) as excinfo:
        policy_update(updated_policies=None, added_policies=None, removed_policies=None)

    CurrentCtx.reset()
    ctx.logger.info("{0} not a node boom: {1}".format(ctx_type, str(excinfo.value)))
    assert ctx_type == 'cloudify.relationships.depends_on'
    assert no_policies == []
    assert str(excinfo.value) == "can only invoke update_policies_on_node on node"

def test_defenses_on_decorators():
    """test defenses of code mainly for code coverage"""
    should_be_none = Policies.gather_policies_to_node()(None)
    assert should_be_none is None

    should_be_none = Policies.update_policies_on_node()(None)
    assert should_be_none is None

def monkeyed_set_policies_boom(policies):
    """monkeypatch for exception"""
    raise Exception("Policies._set_policies boom: {0}".format(json.dumps(policies or {})))

@pytest.fixture()
def fix_boom_gather(monkeypatch):
    """monkeyed boom"""
    monkeypatch.setattr('onap_dcae_dcaepolicy_lib.dcae_policy.Policies._set_policies',
                        monkeyed_set_policies_boom)
    return fix_boom_gather  # provide the fixture value

@cfy_ctx(include_bad=True, include_good=False)
@pytest.mark.usefixtures("fix_boom_gather")
def test_exception_on_gather():
    """test exception on gather"""
    with pytest.raises(NonRecoverableError) as excinfo:
        node_configure()

    ctx.logger.info("monkeyed_set_policies_boom: {0}".format(str(excinfo.value)))
    assert str(excinfo.value).startswith("Failed to set the policies ")

def monkeyed_update_policies_boom(policies):
    """monkeypatch for exception"""
    raise Exception("Policies._update_policies boom")

@pytest.fixture()
def fix_boom_update_policies(monkeypatch):
    """monkeyed boom"""
    monkeypatch.setattr('onap_dcae_dcaepolicy_lib.dcae_policy.Policies._update_policies',
                        monkeyed_update_policies_boom)
    return fix_boom_update_policies  # provide the fixture value

@cfy_ctx(include_bad=True, include_good=False)
@pytest.mark.usefixtures("fix_boom_update_policies")
def test_exception_on_update():
    """test exception on update_policies"""
    with pytest.raises(NonRecoverableError) as excinfo:
        policy_update(updated_policies=None, added_policies=None, removed_policies=None)

    ctx.logger.info("monkeyed_update_policies_boom: {0}".format(str(excinfo.value)))
    assert str(excinfo.value).startswith("Failed to update the policies ")

@cfy_ctx(include_bad=True, include_good=False)
def test_defenses_on_policy_update():
    """test defenses on policy_update"""
    policy_update(updated_policies=None, added_policies=None, removed_policies=None)
    ctx.logger.info("policy_update() ok")

@cfy_ctx(include_bad=True, include_good=False)
def test_defenses_on_set_policies():
    """test defenses of code mainly for code coverage"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    Policies._set_policies({})

    assert dcae_policy.POLICIES not in runtime_properties

    Policies._set_policies({})

    assert dcae_policy.POLICIES not in runtime_properties

@pytest.mark.usefixtures("fix_consul")
@cfy_ctx(include_bad=True)
def test_delete_node():
    """test delete"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    node_delete()


@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_node_no_consul():
    """test delete without consul"""
    node_configure()

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES in runtime_properties
    policies = runtime_properties[dcae_policy.POLICIES]
    ctx.logger.info("policies: {0}".format(json.dumps(policies)))

    node_delete()


@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_node_no_policies():
    """test delete without consul and setup"""

    ctx.instance.runtime_properties[PoliciesOutput.POLICIES_EVENT] = {}
    ctx.instance.runtime_properties[PoliciesOutput.SERVICE_COMPONENT_NAME] = "delete_node_empty"

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES not in runtime_properties

    node_delete()


@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_node_empty():
    """test delete without consul and setup"""
    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES not in runtime_properties

    node_delete()

@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_node_lost_scn():
    """test delete without consul and setup"""
    ctx.instance.runtime_properties[PoliciesOutput.POLICIES_EVENT] = {}

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES not in runtime_properties

    node_delete()


@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_node_empty_config():
    """test delete without consul and setup"""

    ctx.instance.runtime_properties[PoliciesOutput.POLICIES_EVENT] = {}
    ctx.instance.runtime_properties[PoliciesOutput.SERVICE_COMPONENT_NAME] = "delete_node_empty"

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES not in runtime_properties

    node_delete()

@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_ms_no_consul_addr():
    """test delete without consul and setup"""

    ctx.instance.runtime_properties[PoliciesOutput.POLICIES_EVENT] = {}
    ctx.instance.runtime_properties[PoliciesOutput.SERVICE_COMPONENT_NAME] = "delete_node_empty"

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES not in runtime_properties

    node_delete()


@pytest.mark.usefixtures("fix_consul_boom")
@cfy_ctx(include_bad=True)
def test_delete_bad_config():
    """test delete without consul and setup"""

    ctx.instance.runtime_properties[PoliciesOutput.POLICIES_EVENT] = {}
    ctx.instance.runtime_properties[PoliciesOutput.SERVICE_COMPONENT_NAME] = "delete_node_empty"

    runtime_properties = ctx.instance.runtime_properties
    ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

    assert dcae_policy.POLICIES not in runtime_properties

    node_delete()

