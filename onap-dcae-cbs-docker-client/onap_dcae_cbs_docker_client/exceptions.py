# ================================================================================
# Copyright (c) 2019-2021 AT&T Intellectual Property. All rights reserved.
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

""" exceptions used by the Config Binding Server """


class ENVsMissing(Exception):
    """
    Exception to represent critical ENVs are missing
    """

    pass


class CantGetConfig(Exception):
    """
    Configuration could not be fetched likely due to the config not being in Consul
    """

    def __init__(self, code, text):
        self.code = code
        self.text = text

    pass


class CBSUnreachable(Exception):
    """
    CBS was not reachable at all
    """

    pass
