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


set -ex


echo "running script: [$0] for module [$1] at stage [$2]"

MVN_PROJECT_MODULEID="$1"
MVN_PHASE="$2"
PROJECT_ROOT=$(dirname $0)

# expected environment variables
if [ -z "${MVN_NEXUSPROXY}" ]; then
    echo "MVN_NEXUSPROXY environment variable not set.  Cannot proceed"
    exit 1
fi
if [ -z "$SETTINGS_FILE" ]; then
    echo "SETTINGS_FILE environment variable not set.  Cannot proceed"
    exit 2
fi


source "${PROJECT_ROOT}"/mvn-phase-lib.sh


# This is the base for where "deploy" will upload
# MVN_NEXUSPROXY is set in the pom.xml
REPO=$MVN_NEXUSPROXY/content/sites/raw/$MVN_PROJECT_GROUPID

TIMESTAMP=$(date +%C%y%m%dT%H%M%S)
export BUILD_NUMBER="${TIMESTAMP}"


shift 2

case $MVN_PHASE in
clean)
  echo "==> clean phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make clean; else :; fi
    ;;
  *)
    clean_templated_files
    clean_tox_files
    rm -rf ./venv-* ./*.wgn ./site ./coverage.xml ./xunit-results.xml
    ;;
  esac
  ;;
generate-sources)
  echo "==> generate-sources phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make generate-sources; else :; fi
    ;;
  *)
    expand_templates
    ;;
  esac
  ;;
compile)
  echo "==> compile phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make compile; else :; fi
    ;;
  *)
    ;;
  esac
  ;;
test)
  echo "==> test phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make test; else :; fi
    ;;
  *)
    set +e
    run_tox_test
    set -e
    ;;
  esac
  ;;
package)
  echo "==> package phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make package; else :; fi
    ;;
  *)
    ;;
  esac
  ;;
install)
  echo "==> install phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make install; else :; fi
    ;;
  *)
    ;;
  esac
  ;;
deploy)
  echo "==> deploy phase script"
  case $MVN_PROJECT_MODULEID in
  check-blueprint-vs-input | repackage) 
    if [ -f makefile -o -f Makefile ];then make deploy
    else 
      # Upload all files (listed as additional deployment arguments) to Nexus
      # additional
      for artifact
      do
        upload_raw_file $artifact
      done
      set +e +x
    fi
    ;;
  *)
    generate_pypirc_then_publish
    ;;
  esac
  ;;
*)
  echo "==> unprocessed phase"
  ;;
esac

