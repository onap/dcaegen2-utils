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

import time, json, os, re, logging
from itertools import chain
from functools import partial
import requests
import consul
import six
from discovery_client import util


_logger = util.get_logger(__name__)

class DiscoveryInitError(RuntimeError):
    pass

class DiscoveryRegistrationError(RuntimeError):
    pass

class DiscoveryResolvingNameError(RuntimeError):
    pass


#####
# Consul calls for services
#####

def _get_configuration_from_consul(consul_handle, service_name):
    index = None
    while True:
        index, data = consul_handle.kv.get(service_name, index=index)

        if data:
            return json.loads(data["Value"].decode("utf-8"))
        else:
            _logger.warn("No configuration found for {0}. Try again in a bit."
                    .format(service_name))
            time.sleep(5)

def _get_relationships_from_consul(consul_handle, service_name):
    """Fetch the relationship information from Consul for a service by service
    name.  Returns a list of service names."""
    index = None
    rel_key = "{0}:rel".format(service_name)
    while True:
        index, data = consul_handle.kv.get(rel_key, index=index)

        if data:
            return json.loads(data["Value"].decode("utf-8"))
        else:
            _logger.warn("No relationships found for {0}. Try again in a bit."
                    .format(service_name))
            time.sleep(5)

def _lookup_with_consul(consul_handle, service_name, max_attempts=0):
    num_attempts = 1

    while True:
        index, results = consul_handle.catalog.service(service_name)

        if results:
            return results
        else:
            num_attempts += 1

            if max_attempts > 0 and max_attempts < num_attempts:
                return None

            _logger.warn("Service not found {0}. Trying again in a bit."
                    .format(service_name))
            time.sleep(5)

def _register_with_consul(consul_handle, service_name, service_ip, service_port,
        health_endpoint):
    # https://www.consul.io/docs/agent/http/agent.html#agent_service_register
    # Note: Unhealthy services should not return in queries i.e.
    # dig @127.0.0.1 -p 8600 foo.service.consul
    health_url = "http://{0}:{1}/{2}".format(service_ip, service_port, health_endpoint)
    return consul_handle.agent.service.register(service_name, address=service_ip,
            port=service_port, check= { "HTTP": health_url, "Interval": "5s" })

#####
# Config binding service call
#####

def _get_configuration_resolved_from_cbs(consul_handle, service_name):
    """
    This is what a minimal python client library that wraps the CBS would look like.
    POSSIBLE TODO: break this out into pypi repo

    This call does not raise an exception if Consul or the CBS cannot complete the request.
    It logs an error and returns {} if the config is not bindable. 
    It could be a temporary network outage. Call me again later. 

    It will raise an exception if the necessary env parameters were not set because that is irrecoverable.
    This function is called in my /heatlhcheck, so this will be caught early.
    """
    config = {}

    results = _lookup_with_consul(consul_handle, "config_binding_service",
            max_attempts=5)

    if results is None:
        logger.error("Cannot bind config at this time, cbs is unreachable")
    else:
        cbs_hostname = results[0]["ServiceAddress"]
        cbs_port = results[0]["ServicePort"]
        cbs_url = "http://{hostname}:{port}".format(hostname=cbs_hostname, port=cbs_port)

        #get my config
        my_config_endpoint = "{0}/service_component/{1}".format(cbs_url,
                service_name)
        res = requests.get(my_config_endpoint)
        try:
            res.raise_for_status()
            config = res.json()
            _logger.info("get_config returned the following configuration: {0}".format(json.dumps(config)))
        except:
            _logger.error("in get_config, the config binding service endpoint {0} blew up on me. Error code: {1}, Error text: {2}".format(my_config_endpoint, res.status_code, res.text))
    return config

#####
# Functionality for putting together service's configuration
#####

def _get_connection_types(config):
    """Get all the connection types for a given configuration json

    Crawls through the entire config dict recursively and returns the entries
    that have been identified as service connections in the form of a list of tuples -

        [(config key, component type), ..]

    where "config key" is a compound key in the form of a tuple. Each entry in
    the compound key is a key to a level within the json data structure."""
    def grab_component_type(v):
        # To support Python2, unicode strings are not type `str`. Specifically,
        # the config string values from Consul maybe encoded to utf-8 so better
        # be prepared.
        if isinstance(v, six.string_types):
            # Regex matches on strings like "{{foo}}" and "{{ BAR }}" and
            # extracts the alphanumeric string inside the parantheses.
            result = re.match("^{{\s*([-_.\w]*)\s*}}", v)
            return result.group(1) if result else None

    def crawl(config, parent_key=()):
        if isinstance(config, dict):
            rels = [ crawl(value, parent_key + (key, ))
                    for key, value in config.items() ]
            rels = chain(*rels)
        elif isinstance(config, list):
            rels = [ crawl(config[index], parent_key + (index, ))
                    for index in range(0, len(config)) ]
            rels = chain(*rels)
        else:
            rels = [(parent_key, grab_component_type(config))]

        # Filter out the entries with Nones
        rels = [(key, rel) for key, rel in rels if rel]
        return rels

    return crawl(config)

def _has_connections(config):
    return True if _get_connection_types(config) else False

def _resolve_connection_types(service_name, connection_types, relationships):

    def find_match(connection_type):
        ret_list = []
        for rel in relationships:
            if connection_type in rel:
                ret_list.append(rel)
        return ret_list

    return [ (key, find_match(connection_type))
            for key, connection_type in connection_types ]

def _resolve_name(lookup_func, service_name):
    """Resolves the service component name to detailed connection information

    Currently this is grouped into two ways:
    1. CDAP applications take a two step approach - call Consul then call the
    CDAP broker
    2. All other applications just call Consul to get IP and port

    Args:
    ----
    lookup_func: fn(string) -> list of dicts
        The function should return a list of dicts that have "ServiceAddress" and
        "ServicePort" key value entries
    service_name: (string) service name to lookup

    Return depends upon the connection type:
    1. CDAP applications return a dict
    2. All other applications return a string
    """
    def handle_result(result):
        ip = result["ServiceAddress"]
        port = result["ServicePort"]

        if not (ip and port):
            raise DiscoveryResolvingNameError(
                    "Failed to resolve name for {0}: ip, port not set".format(service_name))

        # TODO: Need a better way to identify CDAP apps. Really need to make this
        # better.
        if "platform-" in service_name:
            return "{0}:{1}".format(ip, port)
        elif "cdap" in service_name:
            redirectish_url = "http://{0}:{1}/application/{2}".format(ip, port,
                    service_name)

            r = requests.get(redirectish_url)
            r.raise_for_status()
            details = r.json()
            # Pick out the details to expose to the component developers
            return { key: details[key]
                    for key in ["connectionurl", "serviceendpoints"] }
        else:
            return "{0}:{1}".format(ip, port)

    try:
        results = lookup_func(service_name)
        return [ handle_result(result) for result in results ]
    except Exception as e:
        raise DiscoveryResolvingNameError(
                "Failed to resolve name for {0}: {1}".format(service_name, e))

def _resolve_configuration_dict(ch, service_name, config):
    """
    Helper used by both resolve_configuration_dict and get_configuration
    """
    if _has_connections(config):
        rels = _get_relationships_from_consul(ch, service_name)
        connection_types = _get_connection_types(config)
        connection_names = _resolve_connection_types(service_name, connection_types, rels)
        # NOTE: The hardcoded use of the first element. This is to keep things backwards
        # compatible since resolve name now returns a list.
        for key, conn in [(key, [_resolve_name(partial(_lookup_with_consul, ch), name)[0] for name in names]) for key, names in connection_names]:
            config = util.update_json(config, key, conn)

    _logger.info("Generated config: {0}".format(config))
    return config

#####
# Public calls 
#####

def get_consul_hostname(consul_hostname_override=None):
    """Get the Consul hostname"""
    try:
        return consul_hostname_override \
                if consul_hostname_override else os.environ["CONSUL_HOST"]
    except:
        raise DiscoveryInitError("CONSUL_HOST variable has not been set!")

def get_service_name():
    """Get the full service name

    This is expected to be given from whatever entity is starting this service
    and given by an environment variable called "HOSTNAME"."""
    try:
        return os.environ["HOSTNAME"]
    except:
        raise DiscoveryInitError("HOSTNAME variable has not been set!")


def resolve_name(consul_host, service_name, max_attempts=3):
    """Resolve the service name

    Do a service discovery lookup from Consul and return back the detailed connection
    information.

    Returns:
    --------
    For CDAP apps, returns a dict. All others a string with the format "<ip>:<port>"
    """
    ch = consul.Consul(host=consul_host)
    lookup_func = partial(_lookup_with_consul, ch, max_attempts=max_attempts)
    return _resolve_name(lookup_func, service_name)


def resolve_configuration_dict(consul_host, service_name, config):
    """
    Utility method for taking a given service_name, and config dict, and resolving it
    """
    ch = consul.Consul(host=consul_host)
    return _resolve_configuration_dict(ch, service_name, config)


def get_configuration(override_consul_hostname=None, override_service_name=None,
        from_cbs=True):
    """Provides this service component's configuration information fully resolved

    This method can either resolve the configuration locally here or make a
    remote call to the config binding service. The default is to use the config
    binding service.

    Args:
    -----
    override_consul_hostname (string): Consul hostname to use rather than the one
        set by the environment variable CONSUL_HOST
    override_service_name (string): Use this name over the name set on the
        HOSTNAME environment variable. Default is None.
    from_cbs (boolean): True (default) means use the config binding service otherwise
        set to False to have the config pulled and resolved by this library

    Returns the fully resolved service component configuration as a dict
    """
    # Get config, bootstrap
    consul_hostname = get_consul_hostname(override_consul_hostname)
    # NOTE: We use the default port 8500
    ch = consul.Consul(host=consul_hostname)
    service_name = override_service_name if override_service_name else get_service_name()
    _logger.info("service name: {0}".format(service_name))

    if from_cbs:
        return _get_configuration_resolved_from_cbs(ch, service_name)
    else:
        # The following will happen:
        #
        # 1. Fetching the configuration by service component name from Consul
        # 2. Fetching the relationships for this service component by service component
        # name
        # 3. Pick out the connection types from the templetized fields in the configuration
        # 4. Resolve the connection types with connection names using the step #2
        # information
        # 5. Resolve the connection names with the actual connection via queries to
        # Consul using the connection name
        config = _get_configuration_from_consul(ch, service_name)
        return _resolve_configuration_dict(ch, service_name, config)


def register_for_discovery(consul_host, service_ip, service_port):
    """Register the service component for service discovery

    This is required in order for other services to "discover" you so that you
    can service their requests.

    NOTE: Applications may not need to make this call depending upon if the
    environment is using Registrator.
    """
    ch = consul.Consul(host=consul_host)
    service_name = get_service_name()

    if _register_with_consul(ch, service_name, service_ip, service_port, "health"):
        _logger.info("Registered to consul: {0}".format(service_name))
    else:
        _logger.error("Failed to register to consul: {0}".format(service_name))
        raise DiscoveryRegistrationError()
