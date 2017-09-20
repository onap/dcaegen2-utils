"""setup.py is used for package build and distribution"""

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

from setuptools import setup

setup(
    name='onap_dcae_dcaepolicy_lib',
    description='lib of policy decorators to be used by cloudify plugins of dcae controller',
    version="1.0.0",
    author='Alex Shatov',
    email="dcae@lists.openecomp.org",
    packages=['onap_dcae_dcaepolicy_lib'],
    install_requires=[
    ],
    keywords='policy dcae controller cloudify plugin',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7'
    ]
)
