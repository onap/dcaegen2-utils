#!/bin/bash

# ================================================================================
# Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
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
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.


echo "running script: [$0] for module [$1] at stage [$2]"

echo "=> Prepare environment "
env

# This is the base for where "deploy" will upload
# MVN_NEXUSPROXY is set in the pom.xml
REPO=$MVN_NEXUSPROXY/content/sites/raw/$MVN_PROJECT_GROUPID

TIMESTAMP=$(date +%C%y%m%dT%H%M%S)
export BUILD_NUMBER="${TIMESTAMP}"

# expected environment variables
if [ -z "${MVN_NEXUSPROXY}" ]; then
    echo "MVN_NEXUSPROXY environment variable not set.  Cannot proceed"
    exit
fi
MVN_NEXUSPROXY_HOST=$(echo "$MVN_NEXUSPROXY" |cut -f3 -d'/' | cut -f1 -d':')
echo "=> Nexus Proxy at $MVN_NEXUSPROXY_HOST, $MVN_NEXUSPROXY"

# use the version text detect which phase we are in in LF CICD process: verify, merge, or (daily) release

# mvn phase in life cycle
MVN_PHASE="$2"

case $MVN_PHASE in
clean)
  echo "==> clean phase script"
  if [ -f makefile ];then make clean; fi
  ;;
generate-sources)
  echo "==> generate-sources phase script"
  if [ -f makefile ];then make generate-sources; fi
  ;;
compile)
  echo "==> compile phase script"
  if [ -f makefile ];then make compile; fi
  ;;
test)
  echo "==> test phase script"
  if [ -f makefile ];then make test; fi
  ;;
package)
  echo "==> package phase script"
  if [ -f makefile ];then make package; fi
  ;;
install)
  echo "==> install phase script"
  if [ -f makefile ];then make install; fi
  ;;
deploy)
  echo "==> deploy phase script"
  if [ -f makefile ];then make deploy; fi
  # Just upload files to Nexus
  set -e -x
  function setnetrc {
    # Turn off -x so won't leak the credentials
    set +x
    hostport=$(echo $1 | cut -f3 -d /)
    host=$(echo $hostport | cut -f1 -d:)
    settings=${SETTINGS_FILE:-$HOME/.m2/settings.xml}
    echo machine $host login $(xpath -q -e "//servers/server[id='$MVN_SERVER_ID']/username/text()" $settings) password $(xpath -q -e "//servers/server[id='$MVN_SERVER_ID']/password/text()" $settings) >$HOME/.netrc
    chmod 600 $HOME/.netrc
    set -x
  }
  function putraw {
    curl -X PUT -H "Content-Type: $3" --netrc --upload-file $1 --url $REPO/$2
  }
  setnetrc $REPO
  PLUGIN_FILE=$(echo $PLUGIN_NAME-*.wgn)
  for artifact in $DEPLOYMENT_ARTIFACTS
  do
    putraw $artifact artifacts/$PLUGIN_FILE application/data
  done
  set +e +x
  ;;
*)
  echo "==> unprocessed phase"
  ;;
esac

