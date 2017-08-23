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

import json, logging
# http://stackoverflow.com/questions/9623114/check-if-two-unordered-lists-are-equal
from collections import Counter
from functools import partial
import pytest
import requests
from discovery_client import discovery as dis


def test_get_connection_types():
    config = { "x": "say something", "y": 123, "z": "{{some-analytics}}" }
    expected = [(("z", ), "some-analytics"), ]
    actual = dis._get_connection_types(config)
    assert Counter(expected) == Counter(actual)

    # Whitespaces ok
    config = { "x": "say something", "y": 123, "z": "{{   some-analytics     }}" }
    expected = [(("z", ), "some-analytics"), ]
    actual = dis._get_connection_types(config)
    assert Counter(expected) == Counter(actual)

    # Paul wanted the ability to include version so match on more than just one
    # subfield
    config = { "x": "say something", "y": 123, "z": "{{1-0-0.some-analytics}}" }
    expected = [(("z", ), "1-0-0.some-analytics"), ]
    actual = dis._get_connection_types(config)
    assert Counter(expected) == Counter(actual)

    # Need double parantheses
    config = { "x": "say something", "y": 123, "z": "{some-analytics}" }
    actual = dis._get_connection_types(config)
    assert Counter([]) == Counter(actual)

    # Nested in dict dict
    config = { "x": "say something", "y": 123,
            "z": { "aa":  { "bbb": "{{some-analytics}}" } } }
    expected = [(("z", "aa", "bbb"), "some-analytics"), ]
    actual = dis._get_connection_types(config)
    assert Counter(expected) == Counter(actual)

    # Nested in list dict
    config = { "x": "say something", "y": 123,
            "z": [ "no-op", { "bbb": "{{some-analytics}}" } ] }
    expected = [(("z", 1, "bbb"), "some-analytics"), ]
    actual = dis._get_connection_types(config)
    assert Counter(expected) == Counter(actual)

    # Force strings to be unicode, test for Python2 compatibility
    config = { "x": "say something".decode("utf-8"), "y": 123,
            "z": "{{some-analytics}}".decode("utf-8") }
    expected = [(("z", ), "some-analytics"), ]
    actual = dis._get_connection_types(config)
    assert Counter(expected) == Counter(actual)


def test_resolve_connection_types():
    upstream = "b243b0b8-8a24-4f88-add7-9b530c578149.laika.foobar.rework-central.dcae.ecomp.com"
    downstream = "839b0b31-f13d-4bfc-9adf-450d34071304.laika.foobar.rework-central.dcae.ecomp.com"

    connection_types = [("downstream-laika", "laika"),]
    relationships = [downstream]
    expected = [("downstream-laika", [downstream])]
    actual = dis._resolve_connection_types(upstream, connection_types, relationships)
    assert sorted(actual) == sorted(expected)

    # NOTE: Removed test that tested the scenario where the name stems don't
    # match up. This name stem matching was causing grief to others so lifted the
    # constraint.


def test_resolve_name_for_platform():
    def fake_lookup(fixture, service_name):
        if service_name == fixture["ServiceName"]:
            return [fixture]

    # Good case. Grabbed from Consul call
    fixture = { 'Node': 'agent-one', 'ModifyIndex': 2892, 'Address': '127.0.0.1',
                'ServiceName': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.platform-laika.foobar.rework-central.dcae.ecomp.com',
                'ServicePort': 12708, 'CreateIndex': 2825, 'ServiceAddress': '196.207.143.67',
                'ServiceTags': [], 'ServiceEnableTagOverride': False,
                'ServiceID': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.platform-laika.foobar.rework-central.dcae.ecomp.com'}

    expected = ["{0}:{1}".format(fixture["ServiceAddress"],
        fixture["ServicePort"])]
    assert dis._resolve_name(partial(fake_lookup, fixture), fixture["ServiceName"]) == expected

    # Fail case. When Registrator is misconfigured and ServiceAddress is not set
    fixture = { 'Node': 'agent-one', 'ModifyIndex': 2892, 'Address': '127.0.0.1',
                'ServiceName': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.platform-laika.foobar.rework-central.dcae.ecomp.com',
                'ServicePort': 12708, 'CreateIndex': 2825, 'ServiceAddress': '',
                'ServiceTags': [], 'ServiceEnableTagOverride': False,
                'ServiceID': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.platform-laika.foobar.rework-central.dcae.ecomp.com'}

    with pytest.raises(dis.DiscoveryResolvingNameError):
        dis._resolve_name(partial(fake_lookup, fixture), fixture["ServiceName"])

    # Fail case. When lookup just blows up for some reason
    def fake_lookup_blows(service_name):
        raise RuntimeError("Thar she blows")

    with pytest.raises(dis.DiscoveryResolvingNameError):
        dis._resolve_name(fake_lookup_blows, fixture["ServiceName"])


def test_resolve_name_for_docker():
    def fake_lookup(fixture, service_name):
        if service_name == fixture["ServiceName"]:
            return [fixture]

    # Good case. Grabbed from Consul call
    fixture = { 'Node': 'agent-one', 'ModifyIndex': 2892, 'Address': '127.0.0.1',
                'ServiceName': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.laika.foobar.rework-central.dcae.ecomp.com',
                'ServicePort': 12708, 'CreateIndex': 2825, 'ServiceAddress': '196.207.143.67',
                'ServiceTags': [], 'ServiceEnableTagOverride': False,
                'ServiceID': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.laika.foobar.rework-central.dcae.ecomp.com'}

    expected = ["{0}:{1}".format(fixture["ServiceAddress"],
        fixture["ServicePort"])]
    assert dis._resolve_name(partial(fake_lookup, fixture), fixture["ServiceName"]) == expected

    # Fail case. When Registrator is misconfigured and ServiceAddress is not set
    fixture = { 'Node': 'agent-one', 'ModifyIndex': 2892, 'Address': '127.0.0.1',
                'ServiceName': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.laika.foobar.rework-central.dcae.ecomp.com',
                'ServicePort': 12708, 'CreateIndex': 2825, 'ServiceAddress': '',
                'ServiceTags': [], 'ServiceEnableTagOverride': False,
                'ServiceID': 'e9526e08-f9b8-42c4-99a3-443cd4deeac1.laika.foobar.rework-central.dcae.ecomp.com'}

    with pytest.raises(dis.DiscoveryResolvingNameError):
        dis._resolve_name(partial(fake_lookup, fixture), fixture["ServiceName"])

    # Fail case. When lookup just blows up for some reason
    def fake_lookup_blows(service_name):
        raise RuntimeError("Thar she blows")

    with pytest.raises(dis.DiscoveryResolvingNameError):
        dis._resolve_name(fake_lookup_blows, fixture["ServiceName"])


def test_resolve_name_for_cdap(monkeypatch):
    def fake_lookup(fixture, service_name):
        if service_name == fixture["ServiceName"]:
            return [fixture]

    # Good case. Handle CDAP apps
    fixture = {
            "Node":"agent-one", "Address":"10.170.2.17",
            "ServiceID": "00b6210b71e445cdaadf76e620ebffcfhelloworldcdapappfoobardcaereworkdcaeecompcom",
            "ServiceName": "00b6210b71e445cdaadf76e620ebffcfhelloworldcdapappfoobardcaereworkdcaeecompcom",
            "ServiceTags":[],
            "ServiceAddress": "196.207.143.116",
            "ServicePort": 7777, "ServiceEnableTagOverride": False, "CreateIndex": 144733, "ModifyIndex":145169 }

    class FakeRequestsResponse(object):
        def __init__(self, url, broker_json):
            self.url = url
            self.broker_json = broker_json

        def raise_for_status(self):
            expected_broker_url = "http://{0}:{1}/application/{2}".format(
                    fixture["ServiceAddress"], fixture["ServicePort"],
                    fixture["ServiceName"])
            if self.url == expected_broker_url:
                return True
            else:
                raise RuntimeError("Mismatching address")

        def json(self):
            return self.broker_json

    # Simulate the call to the CDAP broker
    broker_json = {
            "appname":"00b6210b71e445cdaadf76e620ebffcfhelloworldcdapappfoobardcaereworkdcaeecompcom",
            "healthcheckurl":"http://196.207.143.116:7777/application/00b6210b71e445cdaadf76e620ebffcfhelloworldcdapappfoobardcaereworkdcaeecompcom/healthcheck",
            "metricsurl":"http://196.207.143.116:7777/application/00b6210b71e445cdaadf76e620ebffcfhelloworldcdapappfoobardcaereworkdcaeecompcom/metrics",
            "url":"http://196.207.143.116:7777/application/00b6210b71e445cdaadf76e620ebffcfhelloworldcdapappfoobardcaereworkdcaeecompcom",
            "connectionurl":"http://196.207.160.159:10000/v3/namespaces/default/streams/foo",
            "serviceendpoints": "something" }

    monkeypatch.setattr(requests, "get", lambda url: FakeRequestsResponse(url, broker_json))

    expected = [{ key: broker_json[key]
                    for key in ["connectionurl", "serviceendpoints"] }]
    assert dis._resolve_name(partial(fake_lookup, fixture), fixture["ServiceName"]) == expected


def test_resolve_configuration_dict(monkeypatch):
    service_name = "123.current-node-type.some-service.some-location.com"
    target_service_name = "456.target-node-type.some-service.some-location.com"

    # Fake the Consul calls

    def fake_get_relationship(ch, service_name):
        return [ target_service_name ]

    monkeypatch.setattr(dis, "_get_relationships_from_consul",
            fake_get_relationship)

    fixture = [{ 'Node': 'agent-one', 'ModifyIndex': 2892, 'Address': '127.0.0.1',
                 'ServiceName': target_service_name,
                 'ServicePort': 12708, 'CreateIndex': 2825, 'ServiceAddress': '196.207.143.67',
                 'ServiceTags': [], 'ServiceEnableTagOverride': False,
                 'ServiceID': target_service_name }]

    def fake_lookup(ch, service_name):
        return fixture

    monkeypatch.setattr(dis, "_lookup_with_consul", fake_lookup)

    # Simple config case
    test_config = { "target-node": "{{ target-node-type }}", "other-param": 123 }

    expected = dict(test_config)
    expected["target-node"] = ["196.207.143.67:12708"]
    actual = dis._resolve_configuration_dict(None, service_name, test_config)
    assert Counter(actual) == Counter(expected)

    # Nested config case
    test_config = { "output_formats": { "target-node": "{{ target-node-type }}" },
            "other-param": 123 }

    expected = dict(test_config)
    expected["output_formats"]["target-node"] = "196.207.143.67:12708"
    actual = dis._resolve_configuration_dict(None, service_name, test_config)
    assert Counter(actual) == Counter(expected)


def test_get_consul_host(monkeypatch):
    with pytest.raises(dis.DiscoveryInitError):
        dis.get_consul_hostname()

    monkeypatch.setenv("CONSUL_HOST", "i-am-consul-host")
    assert "i-am-consul-host" == dis.get_consul_hostname()

    assert "no-i-am" == dis.get_consul_hostname("no-i-am")
