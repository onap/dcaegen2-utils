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

from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

setup(
        name = "onap-dcae-discovery-client",
        version = "2.1.0",
        packages = find_packages(),
        author = "Michael Hwang",
        email="dcae@lists.openecomp.org",
        description = ("Library of discovery functionality"),
        install_requires = [
            'python-consul>=0.6.0,<1.0.0',
            'requests>=2.11.0,<3.0.0',
            'six>=1.10.0,<2.0.0']
        )
