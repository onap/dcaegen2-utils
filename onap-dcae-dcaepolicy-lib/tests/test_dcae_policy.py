# ============LICENSE_START=======================================================
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
import logging
from datetime import datetime, timedelta

import pytest

from cloudify import ctx
from cloudify.state import current_ctx
from cloudify.exceptions import NonRecoverableError

from mock_cloudify_ctx import MockCloudifyContextFull, TARGET_NODE_ID, TARGET_NODE_NAME
from log_ctx import CtxLogger

from onap_dcae_dcaepolicy_lib import Policies, POLICIES

DCAE_POLICY_TYPE = 'dcae.nodes.policy'
POLICY_ID = 'policy_id'
POLICY_VERSION = "policyVersion"
POLICY_NAME = "policyName"
POLICY_BODY = 'policy_body'
POLICY_CONFIG = 'config'
MONKEYED_POLICY_ID = 'monkeyed.Config_peach'
MONKEYED_POLICY_ID_2 = 'monkeyed.Config_peach_2'
APPLICATION_CONFIG = "application_config"
LOG_FILE = 'test_onap_dcae_dcaepolicy_lib.log'

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
    def create_policy_body(policy_id, policy_version=1):
        """returns a fake policy-body"""
        prev_ver = policy_version - 1
        timestamp = RUN_TS + timedelta(hours=prev_ver)

        prev_ver = str(prev_ver)
        this_ver = str(policy_version)
        config = {
            "policy_updated_from_ver": prev_ver,
            "policy_updated_to_ver": this_ver,
            "policy_hello": "world!",
            "policy_updated_ts": timestamp.isoformat()[:-3] + 'Z',
            "updated_policy_id": policy_id
        }
        return {
            "policyConfigMessage": "Config Retrieved! ",
            "policyConfigStatus": "CONFIG_RETRIEVED",
            "type": "JSON",
            POLICY_NAME: "{0}.{1}.xml".format(policy_id, this_ver),
            POLICY_VERSION: this_ver,
            POLICY_CONFIG: config,
            "matchingConditions": {
                "ECOMPName": "DCAE",
                "ConfigName": "alex_config_name"
            },
            "responseAttributes": {},
            "property": None
        }

    @staticmethod
    def create_policy(policy_id, policy_version=1):
        """returns the whole policy object for policy_id and policy_version"""
        return {
            POLICY_ID : policy_id,
            POLICY_BODY : MonkeyedPolicyBody.create_policy_body(policy_id, policy_version)
        }

    @staticmethod
    def is_the_same_dict(policy_body_1, policy_body_2):
        """check whether both policy_body objects are the same"""
        if not isinstance(policy_body_1, dict) or not isinstance(policy_body_2, dict):
            return False
        for key in policy_body_1.keys():
            if key not in policy_body_2:
                return False
            if isinstance(policy_body_1[key], dict):
                return MonkeyedPolicyBody.is_the_same_dict(
                    policy_body_1[key], policy_body_2[key])
            if (policy_body_1[key] is None and policy_body_2[key] is not None) \
            or (policy_body_1[key] is not None and policy_body_2[key] is None) \
            or (policy_body_1[key] != policy_body_2[key]):
                return False
        return True


class MonkeyedNode(object):
    """node in cloudify"""
    BLUEPRINT_ID = 'test_dcae_policy_bp_id'
    DEPLOYMENT_ID = 'test_dcae_policy_dpl_id'
    EXECUTION_ID = 'test_dcae_policy_exe_id'

    def __init__(self, node_id, node_name, node_type, properties,
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
        MonkeyedLogHandler.add_handler_to(self.ctx.logger)

@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='exe_task')
@Policies.gather_policies_to_node
def node_configure(**kwargs):
    """decorate with @Policies.gather_policies_to_node on policy consumer node to
    bring all policies to runtime_properties["policies"]
    """
    ctx.logger.info("node_configure kwargs: {0}".format(kwargs))

    app_config = None
    if APPLICATION_CONFIG in ctx.node.properties:
        # dockerized blueprint puts the app config into property application_config
        app_config = ctx.node.properties.get(APPLICATION_CONFIG)

    app_config = Policies.shallow_merge_policies_into(app_config)
    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config
    ctx.logger.info("example: applied policy_configs to property app_config: {0}" \
        .format(json.dumps(app_config)))

    policy_configs = Policies.get_policy_configs()
    if policy_configs:
        ctx.logger.warn("TBD: apply policy_configs: {0}".format(json.dumps(policy_configs)))

@CtxLogger.log_ctx(pre_log=True, after_log=True, exe_task='execute_operation')
@Policies.update_policies_on_node(configs_only=True)
def policy_update(updated_policies, **kwargs):
    """decorate with @Policies.update_policies_on_node() to update runtime_properties["policies"]

    :updated_policies: contains the list of changed policy-configs when configs_only=True (default).
    Use configs_only=False to bring the full policy objects in :updated_policies:.

    Use :Policies.shallow_merge_policies_into(): to merge the updated_policies into app_config
    """
    app_config = ctx.instance.runtime_properties[APPLICATION_CONFIG]

    # This is how to merge the policies into app_config object
    app_config = Policies.shallow_merge_policies_into(app_config)

    ctx.logger.info("merged updated_policies {0} into app_config {1}"
                    .format(json.dumps(updated_policies), json.dumps(app_config)))

    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config


def test_policies_to_node():
    """test gather_policies_to_node and policy_update"""

    node_policy = MonkeyedNode(
        'test_dcae_policy_node_id',
        'test_dcae_policy_node_name',
        DCAE_POLICY_TYPE,
        {POLICY_ID: MONKEYED_POLICY_ID},
        None,
        {POLICY_BODY : MonkeyedPolicyBody.create_policy_body(MONKEYED_POLICY_ID)}
    )
    node_policy_2 = MonkeyedNode(
        'test_dcae_policy_node_id_2',
        'test_dcae_policy_node_name_2',
        DCAE_POLICY_TYPE,
        {POLICY_ID: MONKEYED_POLICY_ID_2},
        None,
        {POLICY_BODY : MonkeyedPolicyBody.create_policy_body(MONKEYED_POLICY_ID_2)}
    )
    node_ms = MonkeyedNode('test_ms_id', 'test_ms_name', "ms.nodes.type", None, \
        [{TARGET_NODE_ID: node_policy.node_id, TARGET_NODE_NAME: node_policy.node_name},
         {TARGET_NODE_ID: node_policy_2.node_id, TARGET_NODE_NAME: node_policy_2.node_name}
        ])

    try:
        current_ctx.set(node_ms.ctx)

        node_configure()

        runtime_properties = ctx.instance.runtime_properties
        ctx.logger.info("runtime_properties: {0}".format(json.dumps(runtime_properties)))

        assert POLICIES in runtime_properties
        policies = runtime_properties[POLICIES]
        ctx.logger.info("policies: {0}".format(json.dumps(policies)))

        assert MONKEYED_POLICY_ID in policies
        expected_1 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID)
        policy = policies[MONKEYED_POLICY_ID]
        ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
        ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
        assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
        assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

        assert MONKEYED_POLICY_ID_2 in policies
        expected_2 = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2)
        policy = policies[MONKEYED_POLICY_ID_2]
        ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(expected_2)))
        ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
        assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_2)
        assert MonkeyedPolicyBody.is_the_same_dict(expected_2, policy)

        updated_policy = MonkeyedPolicyBody.create_policy(MONKEYED_POLICY_ID_2, 2)
        ctx.logger.info("policy_update: [{0}]".format(json.dumps(updated_policy)))

        policy_update([updated_policy])

        assert MONKEYED_POLICY_ID_2 in policies
        policy = policies[MONKEYED_POLICY_ID_2]
        ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID_2, json.dumps(policy)))
        assert MonkeyedPolicyBody.is_the_same_dict(policy, updated_policy)
        assert MonkeyedPolicyBody.is_the_same_dict(updated_policy, policy)

        assert MONKEYED_POLICY_ID in policies
        policy = policies[MONKEYED_POLICY_ID]
        ctx.logger.info("expected[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(expected_1)))
        ctx.logger.info("policy[{0}]: {1}".format(MONKEYED_POLICY_ID, json.dumps(policy)))
        assert MonkeyedPolicyBody.is_the_same_dict(policy, expected_1)
        assert MonkeyedPolicyBody.is_the_same_dict(expected_1, policy)

    finally:
        MockCloudifyContextFull.clear()
        current_ctx.clear()
