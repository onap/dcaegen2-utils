#!/bin/sh

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


# nexus has to be listed in ~/.pypirc as repository and contain the url like this
# [nexus]
# repository: https://YOUR_NEXUS_PYPI_SERVER/

case "$1" in
    register)
        echo "python setup.py register -r nexus --show-response"
        python setup.py register -r nexus --show-response
        ;;
    upload)
        echo "python setup.py sdist upload -r nexus --show-response"
        python setup.py sdist upload -r nexus --show-response
        ;;
    build)
        echo "python setup.py sdist register -r nexus --show-response upload -r nexus --show-response"
        python setup.py sdist register -r nexus --show-response upload -r nexus --show-response
        ;;
    *)
        SELF=$(basename "$0")
        echo "Usage:"
        echo "./${SELF} register"
        echo "./${SELF} upload"
        echo "./${SELF} build"
        ;;
esac