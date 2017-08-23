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

import collections
import logging, sys
import six

#####
# Module contains utility methods
#####

def update_json(src, key, value):
    """Updates a nested JSON value

    This method does a recursive lookup for a value given a compound key and then
    replaces that value with the passed in new value.

    For example, given a src json { "a": [ { "aa": 1 }, "foo" ], "b": "2 } and a
    key ("a", 0, "aa"), the value parameter would replace 1.

    :param src: json to update
    :type src: dict or list
    :param key: compound key used to lookup
    :type key: tuple
    :param value: new value used to replace
    :type value: object

    :return: updated json
    """
    if key:
        src[key[0]] = update_json(src[key[0]], key[1:], value)
    else:
        # We've found the value we want to replace regardless of whether or not
        # the object we are replacing is another copmlicated data structure.
        src = value
    return src

def _has_handlers(logger):
    """Check if logger has handlers"""
    if six.PY3:
        return logger.hasHandlers()
    else:
        # TODO: Not sure how to check if a handler has already been attached
        # WATCH: Downside is lines get printed multiple times
        return False

def get_logger(name, level=logging.INFO):
    """Get a logger with sensible defaults

    This method returns a logger from logging by name that has been set with sensible
    defaults if the logger hasn't already been setup with any handlers. The
    default handler is a stream handler to stdout.
    """
    logger = logging.getLogger(name)

    if not _has_handlers(logger):
        # No handlers attached which means logging hasn't been setup. Set
        # "sensible" defaults which means stdout, INFO
        logger.setLevel(level)
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    return logger
