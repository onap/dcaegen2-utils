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

from collections import Counter
from discovery_client import util


def test_update_json():
    # Simple
    test_json = { "a": "{ funk }", "b": "spring" }
    test_key = ("a", )
    test_value = "funk is alive"
    expected = dict(test_json)
    expected["a"] = test_value
    actual = util.update_json(test_json, test_key, test_value)
    assert Counter(expected) == Counter(actual)

    # Nothing to replace, key is empty which translates to repalce the entire
    # json
    test_key = ()
    expected = test_value
    actual = util.update_json(test_json, test_key, test_value)
    assert Counter(expected) == Counter(actual)

    # Nested in dicts
    test_json = { "a": { "aa": { "aaa": "{ funk }", "bbb": "fall" },
        "bb": "summer" }, "b": "spring" }
    test_key = ("a", "aa", "aaa")
    test_value = "funk is alive"
    expected = dict(test_json)
    expected["a"]["aa"]["aaa"] = test_value
    actual = util.update_json(test_json, test_key, test_value)
    assert Counter(expected) == Counter(actual)

    # Nested in dict list
    test_json = { "a": { "aa": [ 123, { "aaa": "{ funk }", "bbb": "fall" } ],
        "bb": "summer" }, "b": "spring" }
    test_key = ("a", "aa", 1, "aaa")
    test_value = "funk is alive"
    expected = dict(test_json)
    expected["a"]["aa"][1]["aaa"] = test_value
    actual = util.update_json(test_json, test_key, test_value)
    assert Counter(expected) == Counter(actual)
