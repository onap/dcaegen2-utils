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

import os
from setuptools import setup, find_packages

setup(
    name='onap-dcae-dockering-lib',
    description='Library used to manage Docker containers in DCAE',
    version="1.3.0",
    author="Michael Hwang",
    author_email="mhwang@research.att.com",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "docker-py>=1.0.0,<2.0.0",
        "six"
    ]
)
