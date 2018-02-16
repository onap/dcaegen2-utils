# org.onap.dcae
# ============LICENSE_START====================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
# =============================================================================
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
# ============LICENSE_END======================================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.

from setuptools import setup, find_packages

setup(
  name='dcaeapplib',
  version='0.0.3',
  packages=find_packages(),
  author = 'Andrew Gauld',
  author_email = 'ag1282@att.com',
  description = ('Library for building DCAE analytics applications'),
  license = 'Apache 2.0',
  keywords = '',
  url = '',
  zip_safe = True,
  install_requires=[ 'onap-dcae-cbs-docker-client>=0.0.2' ],
  entry_points = {
    'console_scripts': [
      'reconfigure.sh=dcaeapplib:reconfigure'
    ]
  }
)
