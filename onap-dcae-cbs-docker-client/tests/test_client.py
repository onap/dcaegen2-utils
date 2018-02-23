# ================================================================================
# Copyright (c) 2017-2018 AT&T Intellectual Property. All rights reserved.
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
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.
from onap_dcae_cbs_docker_client.client import get_config, get_all

class FakeResponse:
    def __init__(self, status_code, thejson):
        self.status_code = status_code
        self.thejson = thejson
    def raise_for_status(self):
        pass
    def json(self):
        return self.thejson

def monkeyed_requests_get(url):
    #mock all the get calls for existent and non-existent
    if url == "http://consuldotcom:8500/v1/catalog/service/config_binding_service":
        return FakeResponse(status_code=200,
                            thejson=[{"ServiceAddress": "666.666.666.666",
                                      "ServicePort": 8888}])
    elif url == "http://666.666.666.666:8888/service_component_all/mybestfrienddotcom":
        return FakeResponse(status_code=200,
                            thejson={"config": {"key_to_your_heart": 666},
                                     "dti": {"some amazing": "dti stuff"},
                                     "policies": {"event": {"foo": "bar"},
                                                  "items": [{"foo2": "bar2"}]},
                                     "otherkey": {"foo3": "bar3"}})

    elif url == "http://666.666.666.666:8888/service_component/mybestfrienddotcom":
        return FakeResponse(status_code=200,
                            thejson={"key_to_your_heart": 666})


def test_config(monkeypatch):
    monkeypatch.setattr('requests.get', monkeyed_requests_get)
    assert(get_config() == {"key_to_your_heart": 666})

def test_all(monkeypatch):
    monkeypatch.setattr('requests.get', monkeyed_requests_get)
    assert(get_all() == {"config": {"key_to_your_heart": 666},
                         "dti": {"some amazing": "dti stuff"},
                         "policies": {"event": {"foo": "bar"},
                                      "items": [{"foo2": "bar2"}]},
                         "otherkey": {"foo3": "bar3"}})
