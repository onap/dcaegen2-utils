# ================================================================================
# Copyright (c) 2017-2021 AT&T Intellectual Property. All rights reserved.
# Copyright (C) 2021 Nokia. All rights reserved.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END=========================================================

""" unit tests for Config Binding Server """

import pytest
import io
import json
import os
import yaml

from unittest.mock import patch

from onap_dcae_cbs_docker_client.client import get_config, get_all
from onap_dcae_cbs_docker_client.client import default_config_path, default_policy_path
from onap_dcae_cbs_docker_client.exceptions import CantGetConfig, CBSUnreachable, ENVsMissing


DEFAULT_REQUESTS_CONFIG = {"key_to_your_heart": 666}
DEFAULT_REQUESTS_CONFIG_ALL = {
    "config": {"key_to_your_heart": 666},
    "dti": {"some amazing": "dti stuff"},
    "policies": {"event": {"foo": "bar"}, "items": [{"foo2": "bar2"}]},
    "otherkey": {"foo3": "bar3"},
}


def test_http(monkeypatch, monkeyed_requests_get):
    monkeypatch.setattr("requests.get", monkeyed_requests_get)

    assert get_config() == DEFAULT_REQUESTS_CONFIG

    assert get_all() == DEFAULT_REQUESTS_CONFIG_ALL


def test_https_url(monkeypatch, monkeyed_requests_get_https):
    """
    this doesn't really test https; because of all the cert stuff,
    however it tests that the url gets formed correctly in the presence of this env variable
    """
    monkeypatch.setattr("requests.get", monkeyed_requests_get_https)
    monkeypatch.setenv("DCAE_CA_CERTPATH", "1")

    assert get_config() == {"key_to_your_heart": 666}

    assert get_all() == {
        "config": {"key_to_your_heart": 666},
        "dti": {"some amazing": "dti stuff"},
        "policies": {"event": {"foo": "bar"}, "items": [{"foo2": "bar2"}]},
        "otherkey": {"foo3": "bar3"},
    }


def test_bad_hostname(monkeypatch, monkeyed_requests_get_404):
    monkeypatch.setattr("requests.get", monkeyed_requests_get_404)
    with pytest.raises(CantGetConfig):
        get_config()
    with pytest.raises(CantGetConfig):
        get_all()

    try:
        get_config()
    except CantGetConfig as e:
        assert e.code == 404
        assert e.text == ""


def test_unreachable(monkeypatch, monkeyed_requests_get_unreachable):
    monkeypatch.setattr("requests.get", monkeyed_requests_get_unreachable)
    with pytest.raises(CBSUnreachable):
        get_config()
    with pytest.raises(CBSUnreachable):
        get_all()


def test_badenv(monkeypatch):
    monkeypatch.delenv("CONFIG_BINDING_SERVICE")
    with pytest.raises(ENVsMissing):
        get_config()
    with pytest.raises(ENVsMissing):
        get_all()


def test_http_with_env(monkeypatch, monkeyed_requests_get_with_env):
    monkeypatch.setattr("requests.get", monkeyed_requests_get_with_env)

    assert get_config() == {"key_to_your_heart": "test_env"}

    assert get_all() == {
        "config": {"key_to_your_heart": "test_env"},
        "dti": {"some amazing": "dti stuff"},
        "policies": {"event": {"foo": "bar"}, "items": [{"foo2": "bar2"}]},
        "otherkey": {"foo3": "bar3"},
    }


def test_https_with_env(monkeypatch, monkeyed_requests_get_https_env):
    monkeypatch.setattr("requests.get", monkeyed_requests_get_https_env)
    monkeypatch.setenv("DCAE_CA_CERTPATH", "1")

    assert get_config() == {"key_to_your_heart": "test_env"}

    assert get_all() == {
        "config": {"key_to_your_heart": "test_env"},
        "dti": {"some amazing": "dti stuff"},
        "policies": {"event": {"foo": "bar"}, "items": [{"foo2": "bar2"}]},
        "otherkey": {"foo3": "bar3"},
    }


def test_http_with_wrong_env(monkeypatch, monkeyed_requests_get_http_with_wrong_env):
    monkeypatch.setattr("requests.get", monkeyed_requests_get_http_with_wrong_env)
    with pytest.raises(ENVsMissing):
        get_config()
    with pytest.raises(ENVsMissing):
        get_all()


################
################
# Tests for using local configuration and profile files.
################
################

# Combinations to test:
# $CBS_CLIENT_CONFIG_PATH set, set to "", not set
# $CBS_CLIENT_POLICY_PATH set, set to "", not set
# config_path file exists, not exists
# policy_path file exists, not exists
# good config, bad config
# good policy, bad policy
# call get_all(), get_config()
# config has ${VAR} to be expanded
# policy does NOT expand ${VAR}

# JSON found in https://jira.onap.org/browse/DCAEGEN2-2753
policy_default = ''.join(['{"policies": {"items": [{"type": "onap.policies.monitoring.tcagen2", ',
                          '"type_version": "1.0.0", "name": "onap.vfirewall.tca", "version": "1.0.0", ',
                          '"metadata": {"policy-id": "onap.vfirewall.tca", "policy-version": "1.0.0"}, ',
                          '"policyName": "onap.vfirewall.tca.1-0-0.xml", "policyVersion": "1.0.0", ',
                          '"config": {"tca.policy": {"domain": "measurementsForVfScaling", ',
                          '"metricsPerEventName": [{"eventName": "vFirewallBroadcastPackets", ',
                          '"controlLoopSchemaType": "VM", "policyScope": "DCAE", "policyName": ',
                          '"DCAE.Config_tca-hi-lo", "policyVersion": "v0.0.1", "thresholds": ',
                          '[{"closedLoopControlName": ',
                          '"ControlLoop-vFirewall-d0a1dfc6-94f5-4fd4-a5b5-4630b438850a", ',
                          '"version": "1.0.2", "fieldPath": ',
                          '"$.event.measurementsForVfScalingFields.vNicPerformanceArray[*].',
                          'receivedTotalPacketsDelta", "thresholdValue": 300, "direction": ',
                          '"LESS_OR_EQUAL", "severity": "MAJOR", "closedLoopEventStatus": ',
                          '"ONSET"}, {"closedLoopControlName": "ControlLoop-vFirewall-d0a1dfc6-',
                          '94f5-4fd4-a5b5-4630b438850a", "version": "1.0.2", "fieldPath": ',
                          '"$.event.measurementsForVfScalingFields.vNicPerformanceArray[*].',
                          'receivedTotalPacketsDelta", "thresholdValue": 700, "direction": ',
                          '"GREATER_OR_EQUAL", "severity": "CRITICAL", "closedLoopEventStatus": ',
                          '"ONSET"}]}]}}}]}, "event": {"action": "gathered", "timestamp": ',
                          '"2021-04-19T23:37:19.709Z", "update_id": "379fb01a-cfe2-4c06-8f6b-',
                          'd51f3c8504af", "policies_count": 1}}'])
found_policy_path = '{"policies": "found policy/path"}'
found_policy_path_with_env = '{"policies": "${POLICYENV}"}'
found_policy_path_with_env_expanded = '{"policies": "pOlIcYeNv"}'
found_policy_path_missing_policy = '{"XXpoliciesXX": "found policy/path"}'
found_config_default = '["found config/default"]'
found_config_default_with_env = '["${CONFIGENV}"]'
found_config_default_with_env_expanded = '["cOnFiGeNv"]'
found_config_path = '["found config/path"]'


class my_mock_open(io.StringIO):
    """
    This class acts like the mock_open function,
    but is able to return different results dependent
    on the path being opened, or even raise different
    exceptions.
    """

    def __init__(self, fname, mode="r"):
        """ Do the right thing for the filename
        """
        ce = os.getenv("CONFIG_EXISTS", "no")
        pe = os.getenv("POLICY_EXISTS", "no")

        # are we a file with data to be returned?
        ret_data = {
            "config/path": [ce, found_config_path],
            "config/env": [ce, found_config_default_with_env],
            default_config_path(): [ce, found_config_default],
            "policy/path": [pe, found_policy_path],
            "policy/env": [pe, found_policy_path_with_env],
            default_policy_path(): [pe, policy_default],
            "bad/policy3": ["yes", found_policy_path_missing_policy],
        }

        if fname in ret_data:
            if ret_data[fname][0] == "yes":
                super().__init__(ret_data[fname][1])
                return

        # These return specifc exceptions
        if fname == "bad/config":
            raise yaml.scanner.ScannerError()
        if fname == "bad/policy":
            raise ValueError()
        if fname == "bad/policy2":
            raise json.decoder.JSONDecodeError(msg="bad json", doc=fname, pos=1)
        if fname == "other/error":
            raise ZeroDivisionError()
            # raise OSError(2, "ENOENT")

        raise FileNotFoundError(fname)


def test_config_file_both_exist(monkeypatch, monkeyed_requests_get):
    """
    These tests cover the cases where both the policy and configuration files exist.
    We vary WHICH file is being pointed at using the environment variables.
    """

    monkeypatch.setattr("requests.get", monkeyed_requests_get)

    monkeypatch.setenv("CONFIG_EXISTS", "yes")
    monkeypatch.setenv("POLICY_EXISTS", "yes")
    monkeypatch.setenv("CONFIGENV", "cOnFiGeNv")
    monkeypatch.setenv("POLICYENV", "pOlIcYeNv")
    for (config_path, expected_config, set_config) in [
            ("config/path", json.loads(found_config_path), True),
            ("config/env", json.loads(found_config_default_with_env_expanded), True),
            ("", json.loads(found_config_default), True),
            (None, json.loads(found_config_default), False)]:

        if set_config:
            monkeypatch.setenv("CBS_CLIENT_CONFIG_PATH", config_path)
        else:
            monkeypatch.delenv("CBS_CLIENT_CONFIG_PATH")

        expected_get_config = expected_config

        for (policy_path, expected_policy, set_policy) in [
                ("policy/path", json.loads(found_policy_path)['policies'], True),
                ("policy/env", json.loads(found_policy_path_with_env)['policies'], True),
                ("", json.loads(policy_default)['policies'], True),
                (None, json.loads(policy_default)['policies'], False)]:

            if set_policy:
                monkeypatch.setenv("CBS_CLIENT_POLICY_PATH", policy_path)
            else:
                monkeypatch.delenv("CBS_CLIENT_POLICY_PATH")

            expected_get_all = {"config": expected_config, "policies": expected_policy}

            with patch('builtins.open', my_mock_open):
                gc = get_config()
                assert gc == expected_get_config

                ga = get_all()
                assert ga == expected_get_all


def test_config_file_config_exists_policy_does_not(monkeypatch, monkeyed_requests_get):
    """
    In this test, the policy file is always missing. Its value is always defaulted to {}.
    The test structure is identical to what we had in test_config_file_both_exist(), but
    the expected configuration to be returned is different.
    """

    monkeypatch.setattr("requests.get", monkeyed_requests_get)

    monkeypatch.setenv("CONFIG_EXISTS", "yes")
    monkeypatch.setenv("POLICY_EXISTS", "no")

    for (config_path, expected_config, set_config) in [
            ("config/path", json.loads(found_config_path), True),
            ("", json.loads(found_config_default), True),
            (None, json.loads(found_config_default), False)]:

        if set_config:
            monkeypatch.setenv("CBS_CLIENT_CONFIG_PATH", config_path)
        else:
            monkeypatch.delenv("CBS_CLIENT_CONFIG_PATH")

        expected_get_config = expected_config
        expected_get_all = {"config": expected_config}

        for (policy_path, expected_policy, set_policy) in [
                ("policy/path", json.loads(found_policy_path)['policies'], True),
                ("", json.loads(policy_default)['policies'], True),
                (None, json.loads(policy_default)['policies'], False)]:

            if set_policy:
                monkeypatch.setenv("CBS_CLIENT_POLICY_PATH", policy_path)
            else:
                monkeypatch.delenv("CBS_CLIENT_POLICY_PATH")

            with patch('builtins.open', my_mock_open):
                gc = get_config()
                assert gc == expected_get_config

                ga = get_all()
                assert ga == expected_get_all


def test_config_file_config_does_not_policy_exists(monkeypatch, monkeyed_requests_get):
    """
    In this test, the config file is always missing. Its value is always defaulted to
    the CBS response.
    The test structure is identical to what we had in test_config_file_both_exist(), but
    the expected configuration to be returned is different.
    """

    monkeypatch.setattr("requests.get", monkeyed_requests_get)

    monkeypatch.setenv("CONFIG_EXISTS", "no")
    monkeypatch.setenv("POLICY_EXISTS", "yes")

    expected_get_config = DEFAULT_REQUESTS_CONFIG
    expected_get_all = DEFAULT_REQUESTS_CONFIG_ALL

    for (config_path, expected_config, set_config) in [
            ("config/path", json.loads(found_config_path), True),
            ("", json.loads(found_config_default), True),
            (None, json.loads(found_config_default), False)]:

        if set_config:
            monkeypatch.setenv("CBS_CLIENT_CONFIG_PATH", config_path)
        else:
            monkeypatch.delenv("CBS_CLIENT_CONFIG_PATH")

        for (policy_path, expected_policy, set_policy) in [
                ("policy/path", json.loads(found_policy_path)['policies'], True),
                ("", json.loads(policy_default)['policies'], True),
                (None, json.loads(policy_default)['policies'], False)]:

            if set_policy:
                monkeypatch.setenv("CBS_CLIENT_POLICY_PATH", policy_path)
            else:
                monkeypatch.delenv("CBS_CLIENT_POLICY_PATH")

            with patch('builtins.open', my_mock_open):
                gc = get_config()
                assert gc == expected_get_config

                ga = get_all()
                assert ga == expected_get_all


def test_config_file_various_exceptions(monkeypatch, monkeyed_requests_get):
    """
    In this test, various forms of exceptions are tested while accessing the
    configuration and policy files.
    Exceptions on the policy file act as if the policy file does not exist.
    Exceptions on the configuration file act as if the configuration file does not exist.
    """

    monkeypatch.setattr("requests.get", monkeyed_requests_get)

    monkeypatch.setenv("CONFIG_EXISTS", "yes")
    monkeypatch.setenv("POLICY_EXISTS", "yes")

    # first do exceptions for the policy file
    for (config_path, expected_config, set_config) in [
            ("config/path", json.loads(found_config_path), True),
            ("", json.loads(found_config_default), True),
            (None, json.loads(found_config_default), False)]:

        if set_config:
            monkeypatch.setenv("CBS_CLIENT_CONFIG_PATH", config_path)
        else:
            monkeypatch.delenv("CBS_CLIENT_CONFIG_PATH")

        expected_get_config = expected_config
        expected_get_all = {"config": expected_config}

        for policy_path in ["bad/policy", "bad/policy2",
                            "bad/policy3", "other/error"]:

            monkeypatch.setenv("CBS_CLIENT_POLICY_PATH", policy_path)

            with patch('builtins.open', my_mock_open):
                gc = get_config()
                assert gc == expected_get_config

                ga = get_all()
                assert ga == expected_get_all

    # next do exceptions for the config file
    expected_get_config = DEFAULT_REQUESTS_CONFIG
    expected_get_all = DEFAULT_REQUESTS_CONFIG_ALL

    policy_path = "policy/path"
    monkeypatch.setenv("CBS_CLIENT_POLICY_PATH", policy_path)

    for config_path in ["bad/config", "other/error"]:

        monkeypatch.setenv("CBS_CLIENT_CONFIG_PATH", config_path)

        with patch('builtins.open', my_mock_open):
            gc = get_config()
            assert gc == expected_get_config

            ga = get_all()
            assert ga == expected_get_all
