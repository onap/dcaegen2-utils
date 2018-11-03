#!/bin/bash

# ================================================================================
# Copyright (c) 2017-2018 AT&T Intellectual Property. All rights reserved.
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


#MVN_PROJECT_MODULEID="$1"
#MVN_PHASE="$2"
#PROJECT_ROOT=$(dirname $0)

FQDN="${MVN_PROJECT_GROUPID}.${MVN_PROJECT_ARTIFACTID}"
if [ "$MVN_PROJECT_MODULEID" == "__" ]; then
  MVN_PROJECT_MODULEID=""
fi

if [[ "$MVN_PROJECT_VERSION" == *SNAPSHOT ]]; then
  echo "=> for SNAPSHOT artifact build"
  MVN_DEPLOYMENT_TYPE='SNAPSHOT'
else
  echo "=> for STAGING/RELEASE artifact build"
  MVN_DEPLOYMENT_TYPE='STAGING'
fi
echo "MVN_DEPLOYMENT_TYPE is             [$MVN_DEPLOYMENT_TYPE]"


TIMESTAMP=$(date +%C%y%m%dT%H%M%S)

# expected environment variables
if [ -z "${MVN_NEXUSPROXY}" ]; then
    echo "MVN_NEXUSPROXY environment variable not set.  Cannot proceed"
    exit
fi
MVN_NEXUSPROXY_HOST=$(echo "$MVN_NEXUSPROXY" |cut -f3 -d'/' | cut -f1 -d':')
echo "=> Nexus Proxy at $MVN_NEXUSPROXY_HOST, $MVN_NEXUSPROXY"

if [ -z "$WORKSPACE" ]; then
    WORKSPACE=$(pwd)
fi

export SETTINGS_FILE=${SETTINGS_FILE:-$HOME/.m2/settings.xml}

RELEASE_TAG=${MVN_RELEASE_TAG:-R4}
if [ "$RELEASE_TAG" == "R1" ]; then
  unset RELEASE_TAG
fi


# mvn phase in life cycle
MVN_PHASE="$2"

echo "MVN_RELEASE_TAG is                 [$MVN_RELEASE_TAG]"
echo "MVN_PROJECT_MODULEID is            [$MVN_PROJECT_MODULEID]"
echo "MVN_PHASE is                       [$MVN_PHASE]"
echo "MVN_PROJECT_GROUPID is             [$MVN_PROJECT_GROUPID]"
echo "MVN_PROJECT_ARTIFACTID is          [$MVN_PROJECT_ARTIFACTID]"
echo "MVN_PROJECT_VERSION is             [$MVN_PROJECT_VERSION]"
echo "MVN_NEXUSPROXY is                  [$MVN_NEXUSPROXY]"
echo "MVN_RAWREPO_BASEURL_UPLOAD is      [$MVN_RAWREPO_BASEURL_UPLOAD]"
echo "MVN_RAWREPO_BASEURL_DOWNLOAD is    [$MVN_RAWREPO_BASEURL_DOWNLOAD]"
MVN_RAWREPO_HOST=$(echo "$MVN_RAWREPO_BASEURL_UPLOAD" | cut -f3 -d'/' |cut -f1 -d':')
echo "MVN_RAWREPO_HOST is                [$MVN_RAWREPO_HOST]"
echo "MVN_RAWREPO_SERVERID is            [$MVN_RAWREPO_SERVERID]"
echo "MVN_DOCKERREGISTRY_SNAPSHOT is     [$MVN_DOCKERREGISTRY_SNAPSHOT]"
echo "MVN_DOCKERREGISTRY_PUBLIC is       [$MVN_DOCKERREGISTRY_PUBLIC]"
echo "MVN_DOCKERREGISTRY_RELEASE is      [$MVN_DOCKERREGISTRY_RELEASE]"
echo "MVN_PYPISERVER_SERVERID            [$MVN_PYPISERVER_SERVERID]"
echo "MVN_PYPISERVER_BASEURL is          [$MVN_PYPISERVER_BASEURL]"



clean_templated_files() 
{
  TEMPLATE_FILES=$(find . -name "*-template")
  for F in $TEMPLATE_FILES; do
    F2=$(echo "$F" | sed 's/-template$//')
    rm -f "$F2"
  done
}
clean_tox_files() 
{
  TOX_FILES=$(find . -name ".tox")
  TOX_FILES="$TOX_FILES $(find . -name 'venv-tox')"
  for F in $TOX_FILES; do
    rm -rf "$F"
  done
}

expand_templates() 
{
  set +x
  # set up env variables, get ready for template resolution
  # NOTE: CCSDK artifacts do not distinguish REALESE vs SNAPSHOTs
  export ONAPTEMPLATE_RAWREPOURL_org_onap_ccsdk_platform_plugins_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.ccsdk.platform.plugins"
  export ONAPTEMPLATE_RAWREPOURL_org_onap_ccsdk_platform_plugins_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.ccsdk.platform.plugins"
  export ONAPTEMPLATE_RAWREPOURL_org_onap_ccsdk_platform_blueprints_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.ccsdk.platform.blueprints"
  export ONAPTEMPLATE_RAWREPOURL_org_onap_ccsdk_platform_blueprints_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.ccsdk.platform.blueprints"


  if [ -z "$RELEASE_TAG" ]; then
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2/releases"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2/snapshots"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_plugins_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.plugins/releases"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_plugins_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.plugins/snapshots"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_blueprints_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.blueprints/releases"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_blueprints_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.blueprints/snapshots"
  else
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2/$RELEASE_TAG"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2/$RELEASE_TAG"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_plugins_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.plugins/$RELEASE_TAG"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_plugins_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.plugins/$RELEASE_TAG"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_blueprints_releases="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.blueprints/$RELEASE_TAG"
    export ONAPTEMPLATE_RAWREPOURL_org_onap_dcaegen2_platform_blueprints_snapshots="$MVN_RAWREPO_BASEURL_DOWNLOAD/org.onap.dcaegen2.platform.blueprints/$RELEASE_TAG"
  fi


  export ONAPTEMPLATE_PYPIURL_org_onap_dcaegen2="${MVN_PYPISERVER_BASEURL}"

  # docker registry templates are for poll, so use PUBLIC registry
  export ONAPTEMPLATE_DOCKERREGURL_org_onap_dcaegen2_releases="${MVN_DOCKERREGISTRY_PUBLIC}"
  export ONAPTEMPLATE_DOCKERREGURL_org_onap_dcaegen2_snapshots="${MVN_DOCKERREGISTRY_PUBLIC}"

  # Mvn repo
  export ONAPTEMPLATE_MVN_org_onap_dcaegen2_analytics_tca_snapshots="${MVN_NEXUSPROXY}/service/local/repositories/snapshots/content/org/onap/dcaegen2/analytics/tca"
  export ONAPTEMPLATE_MVN_org_onap_dcaegen2_analytics_tca_staging="${MVN_NEXUSPROXY}/service/local/repositories/staging/content/org/onap/dcaegen2/analytics/tca"
  export ONAPTEMPLATE_MVN_org_onap_dcaegen2_analytics_tca_releases="${MVN_NEXUSPROXY}/service/local/repositories/releases/content/org/onap/dcaegen2/analytics/tca"


  export ONAPTEMPLATE_STANDARD_INPUTS_TYPES="  # standard inputs list
  centos7image_id:
    type: string
  ubuntu1604image_id:
    type: string
  flavor_id:
    type: string
  security_group:
    type: string
  public_net:
    type: string
  private_net:
    type: string
  openstack: {}
  keypair:
    type: string
  key_filename:
    type: string
  location_prefix:
    type: string
  location_domain:
    type: string
  codesource_url:
    type: string
  codesource_version:
    type: string"


  TEMPLATES=$(env |grep ONAPTEMPLATE | sed 's/=.*//' | sort -u)
  if [ -z "$TEMPLATES" ]; then
    echo "No template variables found!"
    return 0
  fi

  TEMPLATE_FILES=$(find . -name "*-template")
  for F in $TEMPLATE_FILES; do
    F2=$(echo "$F" | sed 's/-template$//')
    cp -p "$F" "$F2"
    chmod u+w "$F2"
   
    echo "====> Resolving the following template from environment variables "
    echo "$TEMPLATES"
    for KEY in $TEMPLATES; do
      VALUE1=$(eval 'echo "$'"$KEY"'"' | sed 1q)
      VALUE2=$(eval 'echo "$'"$KEY"'"' | sed -e 's/\//\\\//g' -e 's/$/\\/' -e '$s/\\$//')

      echo "======> Resolving template $KEY to value $VALUE1 for file $F2"
      sed -i "s/{{[[:space:]]*$KEY[[:space:]]*}}/$VALUE2/g" "$F2"
    done
  done
  echo "====> Done template resolving"
}

test_templates()
{
    # make certain that the type references exist
    TMP=$(mktemp)
    trap 'rm -f $TMP' 0 1 2 3 15

    echo Verify that all of the import URLs are correct
    find . -name '*-template' | sed -e 's/-template$//' |
    while read file
    do
        egrep '^  - .?https?://' < "$file"
    done  | awk '{print $2}' | sed -e 's/"//g' | sort -u |
    while read url
    do
	curl -L -w '%{http_code}' -s -o /dev/null "$url" > "$TMP"
	case $(< "$TMP") in
	    2* ) ;;
	    * ) echo ">>>>>>>>>>>>>>>> $url not found <<<<<<<<<<<<<<<<" ;;
	esac
    done

    echo Verify that the inputs are correct
    PATH=$PATH:$PWD/check-blueprint-vs-input/bin
    find . -name '*-template' | sed -e 's/-template$//' |
    while read blueprint
    do
	check-blueprint-vs-input -b "$blueprint" -i check-blueprint-vs-input/lib/sample-inputs.yaml || true
    done
}


run_tox_test() 
{ 
  set -e -x
  CURDIR=$(pwd)
  TOXINIS=$(find . -name "tox.ini")
  for TOXINI in "${TOXINIS[@]}"; do
    DIR=$(echo "$TOXINI" | rev | cut -f2- -d'/' | rev)
    cd "${CURDIR}/${DIR}"
    rm -rf ./venv-tox ./.tox
    virtualenv ./venv-tox
    source ./venv-tox/bin/activate
    pip install pip==9.0.3
    pip install --upgrade argparse
    pip install tox==2.9.1
    pip freeze
    tox
    deactivate
    rm -rf ./venv-tox ./.tox
  done
}

build_wagons() 
{
  rm -rf ./*.wgn venv-pkg
  SETUPFILES=$(find . -name "setup.py")
  
  virtualenv ./venv-pkg
  source ./venv-pkg/bin/activate
  pip install --upgrade pip 
  pip install wagon
  
  CURDIR=$(pwd)
  for SETUPFILE in $SETUPFILES; do
    PLUGIN_DIR=$(dirname "$SETUPFILE")
    PLUGIN_NAME=$(grep 'name' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9a-zA-Z\.]*//g')
    PLUGIN_VERSION=$(grep 'version' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9\.]*//g')

    echo "In $PLUGIN_DIR, build plugin $PLUGIN_NAME, version $PLUGIN_VERSION"

    wagon create -r "${PLUGIN_DIR}/requirements.txt" --format tar.gz "${PLUGIN_DIR}"

    PKG_FILE_NAMES=( "${PLUGIN_NAME}-${PLUGIN_VERSION}"*.wgn )
    echo Built package: "${PKG_FILE_NAMES[@]}"
    cd "$CURDIR"
  done

  deactivate
  rm -rf venv-pkg
}

build_archives_for_wagons() 
{
  rm -rf ./*.tgz ./*.zip venv-pkg
  
  SETUPFILES=$(find "$(pwd)" -name "setup.py")
  CURDIR=$(pwd)
  for SETUPFILE in $SETUPFILES; do
    PLUGIN_FULL_DIR=$(dirname "$SETUPFILE")
    PLUGIN_BASE_DIR=$(basename "$PLUGIN_FULL_DIR")
    PLUGIN_NAME=$(grep 'name' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9a-zA-Z\.]*//g')
    PLUGIN_VERSION=$(grep 'version' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9\.]*//g')

    cd "${PLUGIN_FULL_DIR}"/..
    echo "In $(pwd), build plugin zip $PLUGIN_NAME, version $PLUGIN_VERSION"

    zip -r "${PLUGIN_NAME}-${PLUGIN_VERSION}.zip" "./${PLUGIN_BASE_DIR}"
    tar -czvf "${PLUGIN_NAME}-${PLUGIN_VERSION}.tgz" "./${PLUGIN_BASE_DIR}"

    echo "Built archives for package ${PLUGIN_NAME}-${PLUGIN_VERSION} at $(pwd)"
    cd "$CURDIR"
  done
}


upload_raw_file() 
{
  # Extract the username and password to the nexus repo from the settings file
  USER=$(xpath -q -e "//servers/server[id='$MVN_RAWREPO_SERVERID']/username/text()" "$SETTINGS_FILE")
  PASS=$(xpath -q -e "//servers/server[id='$MVN_RAWREPO_SERVERID']/password/text()" "$SETTINGS_FILE")
  NETRC=$(mktemp)
  echo "machine $MVN_RAWREPO_HOST login $USER password $PASS" > "$NETRC"

  REPO="$MVN_RAWREPO_BASEURL_UPLOAD"

  OUTPUT_FILE=$1
  EXT=$(echo "$OUTPUT_FILE" | rev |cut -f1 -d '.' |rev)
  if [ "$EXT" == 'yaml' ]; then
    OUTPUT_FILE_TYPE='text/x-yaml'
  elif [ "$EXT" == 'sh' ]; then
    OUTPUT_FILE_TYPE='text/x-shellscript'
  elif [ "$EXT" == 'gz' ]; then
    OUTPUT_FILE_TYPE='application/gzip'
  elif [ "$EXT" == 'tgz' ]; then
    OUTPUT_FILE_TYPE='application/gzip'
  elif [ "$EXT" == 'zip' ]; then
    OUTPUT_FILE_TYPE='application/zip'
  elif [ "$EXT" == 'wgn' ]; then
    OUTPUT_FILE_TYPE='application/gzip'
  else
    OUTPUT_FILE_TYPE='application/octet-stream'
  fi

  # for multi module projects, the raw repo path must match with project name, not project + module
  # FQDN is project + module
  # GROUPID is project name
  if [ "$MVN_PROJECT_ARTIFACTID" == "$MVN_PROJECT_MODULEID" ]; then
    PROJECT_NAME=${MVN_PROJECT_GROUPID}
  else
    PROJECT_NAME=${FQDN}
  fi

  if [ -z "$RELEASE_TAG" ]; then
    SEND_TO="${REPO}/${PROJECT_NAME}"
  else
    SEND_TO="${REPO}/${PROJECT_NAME}/${RELEASE_TAG}"
  fi
 
  if [ ! -z "$2" ]; then
    SEND_TO="$SEND_TO/$2"
  fi

  echo "Sending ${OUTPUT_FILE} to Nexus: ${SEND_TO}"
  curl -vkn --netrc-file "${NETRC}" --upload-file "${OUTPUT_FILE}" -X PUT -H "Content-Type: $OUTPUT_FILE_TYPE" "${SEND_TO}/${OUTPUT_FILE}-${TIMESTAMP}"
  curl -vkn --netrc-file "${NETRC}" --upload-file "${OUTPUT_FILE}" -X PUT -H "Content-Type: $OUTPUT_FILE_TYPE" "${SEND_TO}/${OUTPUT_FILE}"
}

upload_wagon_archives()
{
  SETUPFILES=$(find "$(pwd)" -name "setup.py")
  CURDIR=$(pwd)
  for SETUPFILE in $SETUPFILES; do
    PLUGIN_FULL_DIR=$(dirname "$SETUPFILE")
    PLUGIN_BASE_DIR=$(basename "$PLUGIN_FULL_DIR")
    PLUGIN_NAME=$(grep 'name' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9a-zA-Z\.]*//g')
    PLUGIN_VERSION=$(grep 'version' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9\.]*//g')

    cd "${PLUGIN_FULL_DIR}"/..
    echo "In $(pwd), upload zip archive for $PLUGIN_NAME, version $PLUGIN_VERSION"
    ARCHIVE_FILE_NAME="${PLUGIN_NAME}-${PLUGIN_VERSION}.zip" 
    if [ -z "$ARCHIVE_FILE_NAME" ]; then
      echo "!!! No zip archive file found ${ARCHIVE_FILE_NAME}"
      exit -1
    fi
    upload_raw_file "${ARCHIVE_FILE_NAME}" "${PLUGIN_NAME}/${PLUGIN_VERSION}"

    echo "In $(pwd), upload tgz archive for $PLUGIN_NAME, version $PLUGIN_VERSION"
    ARCHIVE_FILE_NAME="${PLUGIN_NAME}-${PLUGIN_VERSION}.tgz"
    if [ -z "$ARCHIVE_FILE_NAME" ]; then
      echo "!!! No tgz archive file found ${ARCHIVE_FILE_NAME}"
      exit -1
    fi
    upload_raw_file "${ARCHIVE_FILE_NAME}" "${PLUGIN_NAME}/${PLUGIN_VERSION}"

    cd "${CURDIR}"
  done
}

upload_wagons_and_type_yamls()
{
  SETUPFILES=$(find . -name "setup.py")

  CURDIR=$(pwd)
  for SETUPFILE in $SETUPFILES; do
    PLUGIN_DIR=$(dirname "$SETUPFILE")
    PLUGIN_NAME=$(grep 'name' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9a-zA-Z\.]*//g')
    PLUGIN_VERSION=$(grep 'version' "$SETUPFILE" | cut -f2 -d'=' | sed 's/[^0-9\.]*//g')
    PLUGIN_VERSION_MAJOR=$(echo "$PLUGIN_VERSION" | cut -f1 -d'.')
    PLUGIN_VERSION_MAJOR_MINOR=$(echo "$PLUGIN_VERSION" | cut -f1-2 -d'.')

    echo "Found setup file in $PLUGIN_DIR, for plugin $PLUGIN_NAME version $PLUGIN_VERSION"

    TYPEFILE_NAME=$(grep -R "package_name:[[:space:]]*${PLUGIN_NAME}" | cut -f1 -d ':')
    if [ -z "$TYPEFILE_NAME" ]; then
      echo "!!! No typefile found with matching package name $PLUGIN_NAME"
      exit -1
    fi
    NEWFILENAME="${PLUGIN_NAME}"_types.yaml
    if [ "$TYPEFILE_NAME" != "$NEWFILENAME" ]; then
      echo "copy typefile to standard naming"
      cp -f "$TYPEFILE_NAME" "$NEWFILENAME"
    fi

    TYPEFILE_PACKAGE_VERSION=$(grep -R 'package_version' "$TYPEFILE_NAME" |cut -f2 -d ':' |sed -r 's/\s+//g')
    WAGONFILE_NAME=$(ls -1 "${PLUGIN_NAME}"-"${TYPEFILE_PACKAGE_VERSION}"-*.wgn)
    if [ -z "$WAGONFILE_NAME" ]; then
      echo "!!! No wagonfile found with matching package name and version as required in typefile: "
      echo "    $TYPEFILE_NAME plugin $PLUGIN_NAME package version ${TYPEFILE_PACKAGE_VERSION}"
      exit -1
    fi

    upload_raw_file "${NEWFILENAME}" "${PLUGIN_NAME}/${PLUGIN_VERSION}"
    upload_raw_file "${WAGONFILE_NAME}" "${PLUGIN_NAME}/${PLUGIN_VERSION}"
   
    rm -r "$WAGONFILE_NAME"
    if [ "$TYPEFILE_NAME" != "$NEWFILENAME" ]; then
      rm -f "$NEWFILENAME"
    fi
  done
}

upload_files_of_extension()
{
  FILES=$(ls -1 ./*."$1")
  for F in $FILES ; do
    upload_raw_file "$F" "$2"
  done
}
upload_files_of_extension_recursively()
{
  FILES=$(find . -name "*.$1")
  for F in $FILES ; do
    upload_raw_file "$F" "$2"
  done
}


generate_pypirc_then_publish() 
{
  set +x
  USER=$(xpath -e "//servers/server[id='$MVN_PYPISERVER_SERVERID']/username/text()" "$SETTINGS_FILE")
  PASS=$(xpath -e "//servers/server[id='$MVN_PYPISERVER_SERVERID']/password/text()" "$SETTINGS_FILE")

  if [[ "$MVN_PYPISERVER_BASEURL" != */ ]]; then
    MVN_PYPISERVER_BASEURL="${MVN_PYPISERVER_BASEURL}/"
  fi
 

  cat > ~/.pypirc <<EOL
[distutils]
index-servers = 
  $MVN_PYPISERVER_SERVERID
 
[$MVN_PYPISERVER_SERVERID]
repository: $MVN_PYPISERVER_BASEURL
username: $USER
password: $PASS
EOL

  # this may fail if a package of same version exists
  python setup.py sdist register -r "$MVN_PYPISERVER_SERVERID" upload -r "$MVN_PYPISERVER_SERVERID"
  set -x
}



# following the https://wiki.onap.org/display/DW/Independent+Versioning+and+Release+Process
#IndependentVersioningandReleaseProcess-StandardizedDockerTagging
build_and_push_docker()
{
  # Old tagging 
  #IMAGENAME="onap/${FQDN}.${MVN_PROJECT_MODULEID}"
  # new tagging
  ENDID=$(echo $FQDN | rev | cut -f1 -d '.' |rev)
  if [ "$ENDID" == "${MVN_PROJECT_MODULEID}" ]; then
    #IMAGENAME="onap/${FQDN/org.onap./}"
    IMAGENAME="onap/${FQDN}"
  else
    #IMAGENAME="onap/${FQDN/org.onap./}.${MVN_PROJECT_MODULEID}"
    IMAGENAME="onap/${FQDN}.${MVN_PROJECT_MODULEID}"
  fi 

  IMAGENAME=$(echo "$IMAGENAME" | sed -e 's/_*$//g' -e 's/\.*$//g')
  IMAGENAME=$(echo "$IMAGENAME" | tr '[:upper:]' '[:lower:]')

  # use the major and minor version of the MVN artifact version as docker image version
  VERSION="${MVN_PROJECT_VERSION//[^0-9.]/}"
  VERSION2=$(echo "$VERSION" | cut -f1-2 -d'.')

  LFQI="${IMAGENAME}:${VERSION}-${TIMESTAMP}"Z
  # build a docker image
  docker build --rm -f ./Dockerfile -t "${LFQI}" ./

  # all local builds push to SNAPSHOT repo
  REPO=""
  if [ $MVN_DEPLOYMENT_TYPE == "SNAPSHOT" ]; then
     REPO=$MVN_DOCKERREGISTRY_SNAPSHOT
  elif [ $MVN_DEPLOYMENT_TYPE == "STAGING" ]; then
     REPO=$MVN_DOCKERREGISTRY_SNAPSHOT
  else
     echo "Fail to determine DEPLOYMENT_TYPE"
     REPO=$MVN_DOCKERREGISTRY_SNAPSHOT
  fi
  echo "DEPLOYMENT_TYPE is: $MVN_DEPLOYMENT_TYPE, repo is $REPO"

  if [ ! -z "$REPO" ]; then
    USER=$(xpath -e "//servers/server[id='$REPO']/username/text()" "$SETTINGS_FILE")
    PASS=$(xpath -e "//servers/server[id='$REPO']/password/text()" "$SETTINGS_FILE")
    if [ -z "$USER" ]; then
      echo "Error: no user provided"
    fi
    if [ -z "$PASS" ]; then
      echo "Error: no password provided"
    fi
    [ -z "$PASS" ] && PASS_PROVIDED="<empty>" || PASS_PROVIDED="<password>"
    echo docker login "$REPO" -u "$USER" -p "$PASS_PROVIDED"
    docker login "$REPO" -u "$USER" -p "$PASS"

    # local tag is imagename:version-timestamp
    OLDTAG="${LFQI}" 
    # three tags are pushed:  
    #   {imagename}:{semver}-SNAPSHOT-{timestamp}Z       this is what CIMAN-132 asks
    #   {imagename}:{semver}                             latest of current version, for testing
    #   {imagename}:latest                               latest of all, used mainly by csit
    # LFQI="${IMAGENAME}:${VERSION}-${TIMESTAMP}"Z
    PUSHTAGS="${REPO}/${IMAGENAME}:${VERSION}-SNAPSHOT-${TIMESTAMP}Z ${REPO}/${IMAGENAME}:${VERSION} ${REPO}/${IMAGENAME}:latest"
    for NEWTAG in ${PUSHTAGS}
    do
      echo "tagging ${OLDTAG} to ${NEWTAG}"
      docker tag "${OLDTAG}" "${NEWTAG}"
      echo "pushing ${NEWTAG}"
      docker push "${NEWTAG}"
      OLDTAG="${NEWTAG}"
    done
  fi
}
