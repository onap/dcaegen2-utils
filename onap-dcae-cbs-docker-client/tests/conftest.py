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
import pytest
from requests.exceptions import HTTPError, ConnectionError


class FakeResponse:
    def __init__(self, status_code, thejson):
        self.status_code = status_code
        self.thejson = thejson
        self.text = ""

    def raise_for_status(self):
        if self.status_code > 299:
            raise HTTPError

    def json(self):
        return self.thejson


good_resp_all = FakeResponse(
    status_code=200,
    thejson={
        "config": {"key_to_your_heart": 666},
        "dti": {"some amazing": "dti stuff"},
        "policies": {"event": {"foo": "bar"}, "items": [{"foo2": "bar2"}]},
        "otherkey": {"foo3": "bar3"},
    },
)
good_resp_conf = FakeResponse(status_code=200, thejson={"key_to_your_heart": 666})


@pytest.fixture
def monkeyed_requests_get():
    """
    mock for the CBS get
    """

    def _monkeyed_requests_get(url):
        if url == "http://config-binding-service:10000/service_component_all/testhostname":
            return good_resp_all
        elif url == "http://config-binding-service:10000/service_component/testhostname":
            return good_resp_conf
        else:
            raise Exception("Unexpected URL {0}!".format(url))

    return _monkeyed_requests_get


@pytest.fixture
def monkeyed_requests_get_https():
    """
    mock for the CBS get
    """

    def _monkeyed_requests_get_https(url, verify=""):
        if url == "https://config-binding-service:10443/service_component_all/testhostname":
            return good_resp_all
        elif url == "https://config-binding-service:10443/service_component/testhostname":
            return good_resp_conf
        else:
            raise Exception("Unexpected URL {0}!".format(url))

    return _monkeyed_requests_get_https


@pytest.fixture
def monkeyed_requests_get_404():
    def _monkeyed_requests_get_404(url):
        """
        get that pretends that key doesnt exist
        """
        if url in [
            "http://config-binding-service:10000/service_component_all/testhostname",
            "http://config-binding-service:10000/service_component/testhostname",
        ]:
            return FakeResponse(status_code=404, thejson={})
        raise Exception("Unexpected URL {0}!".format(url))

    return _monkeyed_requests_get_404


@pytest.fixture
def monkeyed_requests_get_unreachable():
    def _monkeyed_requests_get_unreachable(_url):
        raise ConnectionError()

    return _monkeyed_requests_get_unreachable
