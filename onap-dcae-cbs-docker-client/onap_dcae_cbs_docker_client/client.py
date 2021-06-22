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

""" provide a means to return a configuration to CBS """

import json
import os
import requests
import sys
import yaml

from onap_dcae_cbs_docker_client import get_module_logger
from onap_dcae_cbs_docker_client.exceptions import ENVsMissing, CantGetConfig, CBSUnreachable

logger = get_module_logger(__name__)


DEFAULT_CONFIG_PATH = "/app-config/application_config.yaml"
DEFAULT_POLICY_PATH = "/etc/policies/policies.json"


# provide a means to import the default paths into unit tests
# For some reason, tox does not like
# from onap_dcae_cbs_docker_client.client import DEFAULT_CONFIG_PATH, DEFAULT_POLICY_PATH

def default_config_path():
    return DEFAULT_CONFIG_PATH


def default_policy_path():
    return DEFAULT_POLICY_PATH

#########
# HELPERS


def _recurse(config):
    """
    Recurse through a configuration, or recursively a sub element of it.
    If it's a dict: recurse over all the values
    If it's a list: recurse over all the values
    If it's a string: expand the string and return its replacement
    If none of the above, just return the item.
    """
    if isinstance(config, list):
        return [_recurse(item) for item in config]
    if isinstance(config, dict):
        for key in config:
            config[key] = _recurse(config[key])
        return config
    if isinstance(config, str):
        return change_envs(config)
    # not a dict, not a list, not a string, nothing to do.
    return config


def _get_path(path):
    """
    Try to get the config, and return appropriate exceptions otherwise
    """
    try:
        hostname = os.environ["HOSTNAME"]  # this is the name of the component itself
        # in most cases, this is the K8s service name which is a resolvable DNS name
        # if running outside k8s, this name needs to be resolvable by DNS via other means.
        cbs_name = os.environ["CONFIG_BINDING_SERVICE"]
    except KeyError as e:
        raise ENVsMissing("Required ENV Variable {0} missing".format(e))

    # See if we are using https
    https_cacert = os.environ.get("DCAE_CA_CERTPATH", None)

    # Get the CBS URL.
    cbs_url = "https://{0}:10443".format(cbs_name) if https_cacert else "http://{0}:10000".format(cbs_name)

    # get my config
    try:
        my_config_endpoint = "{0}/{1}/{2}".format(cbs_url, path, hostname)
        res = requests.get(my_config_endpoint, verify=https_cacert) if https_cacert else requests.get(my_config_endpoint)
        res.raise_for_status()
        config = res.json()
        logger.debug(
            "get_config returned the following configuration: %s using the config url %s",
            json.dumps(config),
            my_config_endpoint,
        )
        return config
    except requests.exceptions.HTTPError:  # this is thrown by raise_for_status
        logger.error(
            "The config binding service endpoint %s returned a bad status. code: %d, text: %s",
            my_config_endpoint,
            res.status_code,
            res.text,
        )
        raise CantGetConfig(res.status_code, res.text)
    except requests.exceptions.ConnectionError as e:  # this is thrown if requests.get cant even connect to the endpoint
        raise CBSUnreachable(e)


def change_envs(value):
    """
    Replace env reference by actual value and return it
    """
    if value.startswith('${'):
        name = value[2:-1]
        if name in os.environ:
            return os.environ[name]

        logger.error(f"Required ENV Variable '{name}' missing. Is '{value}' properly formatted?")
        raise ENVsMissing(f"Required ENV Variable {name} missing. Is '{value}' properly formatted?")
    return value


#########
# Public
def get_all():
    """
    If not configured locally,
    hit the CBS service_component_all endpoint

    Local configuration comes from $CBS_CLIENT_CONFIG_PATH and $CBS_CLIENT_POLICY_PATH,
    defaulted to /app-config/application_config.yaml and /etc/policies/policies.json.
    """
    config_path = os.getenv("CBS_CLIENT_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    if config_path == "":
        config_path = DEFAULT_CONFIG_PATH
    policy_path = os.getenv("CBS_CLIENT_POLICY_PATH", DEFAULT_POLICY_PATH)
    if policy_path == "":
        policy_path = DEFAULT_POLICY_PATH

    try:
        logger.debug(f"opening config_path={config_path}")
        with open(config_path) as fp:
            config = yaml.safe_load(fp)

        policies = None
        try:
            logger.debug(f"opening policy_path={policy_path}")
            with open(policy_path) as fp:
                policies = json.load(fp)

        except FileNotFoundError:
            logger.debug("Policy File Not Found exception received")
            pass

        except (json.decoder.JSONDecodeError, ValueError) as e:
            logger.error(f"The policy file '{policy_path}' has invalid JSON: %s", e)
            pass

        except Exception as e:
            logger.error(f"An error occurred processing the policy file '{policy_path}': %s", e)
            import traceback
            traceback.print_exc(file=sys.stderr)
            pass

        if policies is not None:
            if "policies" in policies:
                logger.debug(f"Returning config read from {config_path} an policy read from {policy_path}")
                ret = {"config": _recurse(config), "policies": policies["policies"]}
            else:
                logger.error(f"The policy file '{policy_path}' does NOT have a 'policies' block in it.")
                ret = {"config": _recurse(config)}
        else:
            logger.debug(f"Returning config read from {config_path}")
            ret = {"config": _recurse(config)}

        return ret

    except yaml.scanner.ScannerError as e:
        logger.error(f"The configuration file '{config_path}' has invalid YAML: {e}")
        pass

    except FileNotFoundError:
        logger.debug("Config File Not Found exception received")
        pass

    except Exception as e:
        logger.error(f"An error occurred processing the configuration file '{config_path}': {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        pass

    logger.debug("Fallback to using REST call")
    config = _get_path("service_component_all")
    return _recurse(config)


def get_config():
    """
    If not configured locally,
    hit the CBS service_component endpoint for the configuration.

    Local configuration comes from $CBS_CLIENT_CONFIG_PATH,
    defaulted to /app-config/application_config.yaml.

    TODO: should we take in a "retry" boolean, and retry on behalf of the caller?
    Currently, we return an exception and let the application decide how it wants to proceed (Crash, try again, etc).
    """
    config_path = os.getenv("CBS_CLIENT_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    if config_path == "":
        config_path = DEFAULT_CONFIG_PATH

    try:
        logger.debug(f"opening config_path={config_path}")
        with open(config_path) as fp:
            config = yaml.safe_load(fp)

        logger.debug(f"Returning config read from {config_path}")
        return _recurse({"config": config})

    except yaml.scanner.ScannerError as e:
        logger.error(f"The configuration file '{config_path}' has invalid YAML: {e}")
        pass

    except FileNotFoundError:
        logger.debug("Config File Not Found exception received")
        pass

    except Exception as e:
        logger.error(f"An error occurred processing the configuration file '{config_path}': {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        pass

    logger.debug("Fallback to using REST call")
    config = _get_path("service_component")
    return _recurse(config)
