# ================================================================================
# Copyright (c) 2017-2021 AT&T Intellectual Property. All rights reserved.
# Copyright (C) 2021 Nokia. All rights reserved.
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

from setuptools import setup, find_packages

setup(
    name="onap_dcae_cbs_docker_client",
    description="very lightweight client for a DCAE dockerized component to get it's config from the CBS",
    version="2.2.0",
    packages=find_packages(),
    author="Tommy Carpenter",
    author_email="tommy@research.att.com",
    license="Apache 2",
    url="https://gerrit.onap.org/r/#/admin/projects/dcaegen2/utils",
    install_requires=["requests>= 2.0.0, < 3.0.0"],
)
