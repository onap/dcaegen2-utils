# ================================================================================
# Copyright (c) 2017-2019 AT&T Intellectual Property. All rights reserved.
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
import pytest
from onap_dcae_cbs_docker_client.client import get_config, get_all
from onap_dcae_cbs_docker_client.exceptions import CantGetConfig, CBSUnreachable, ENVsMissing


def test_http(monkeypatch, monkeyed_requests_get):
    monkeypatch.setattr("requests.get", monkeyed_requests_get)

    assert get_config() == {"key_to_your_heart": 666}

    assert get_all() == {
        "config": {"key_to_your_heart": 666},
        "dti": {"some amazing": "dti stuff"},
        "policies": {"event": {"foo": "bar"}, "items": [{"foo2": "bar2"}]},
        "otherkey": {"foo3": "bar3"},
    }


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
