# org.onap.dcae
# ================================================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
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

"""generic utils to be used by dcae_policy decorators for the policy lifecycle in cloudify"""

from copy import deepcopy
from decimal import Decimal, DecimalException

FIELD_NAME_DELIMITER = ":"
FIELD_TYPE_DELIMITER = "::"
FIELD_TYPE_NUMBER = "number"
KEYWORD_DESC = "desc"
KEYWORD_NULLS_LAST = "nulls-last"

class Utils(object):
    """generic static class used for policy operations"""

    @staticmethod
    def remove_empties(any_list):
        """returns the any_list without empty elements"""
        return [element for element in any_list or [] if element]

    @staticmethod
    def get_field_value(parent, field_path, field_type=None):
        """
        Find and return the field :field_path: under :parent:

        Optionally, converts the field value to field_type.

        Parser of the :field_path: is using the delimiter ":" (semicolon)

        Example:
            parent = ctx.node.properties
            field_path = "docker_config:policy:apply_order"

            will return the value of the apply_order field under the ctx.node.properties in

                properties:
                    docker_config:
                        policy:
                            apply_order
        """
        if not parent or not field_path or not isinstance(parent, dict):
            return

        field_path = Utils.remove_empties([
            path.strip() for path in field_path.split(FIELD_NAME_DELIMITER)
        ])

        if not field_path:
            return

        field_value = None
        field_idx = len(field_path) - 1
        for (idx, field_name) in enumerate(field_path):
            parent = parent.get(field_name)
            if idx == field_idx:
                field_value = deepcopy(parent)
                if field_type in [FIELD_TYPE_NUMBER] and isinstance(field_value, (str, unicode)):
                    try:
                        field_value = Decimal(field_value)
                    except DecimalException:
                        pass
            elif not parent or not isinstance(parent, dict):
                return
        return field_value

    @staticmethod
    def parse_clause_item(clause_item):
        """
        Parses: the :clause_item: in policy_apply_order_clause
        and returns (field_path, field_type, reverse, nulls_last)

        delimiters: are whitespaces, "::"

        nulls-first is the default sorting order

        :clause_item: format is <field_path> [:: <field_type>] [desc] [nulls-last]

        Examples: "config:db_client" versus "config:foo desc" versus
            "matchingConditions:priority::number desc nulls-last"
        """
        field_path = field_type = desc = nulls_last = None

        if not clause_item or not isinstance(clause_item, (str, unicode)):
            return field_path, field_type, bool(desc), bool(nulls_last)

        for idx, token in enumerate(clause_item.split()):
            if idx == 0:
                split_for_type = token.split(FIELD_TYPE_DELIMITER)
                field_path = split_for_type[0]
                field_type = split_for_type[1] if len(split_for_type) > 1 else None
            elif token == KEYWORD_DESC:
                desc = True
            elif token == KEYWORD_NULLS_LAST:
                nulls_last = True
        return field_path, field_type, bool(desc), bool(nulls_last)

    @staticmethod
    def key_with_none_in_sort(reverse, nulls_last, value):
        """
        constructs tuple for proper placement of None values (last versus first)
        in the sorted list of values regardless of the :reverse:
        """
        return reverse == nulls_last or value is None, value
