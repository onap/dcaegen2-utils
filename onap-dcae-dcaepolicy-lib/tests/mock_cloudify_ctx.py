# ============LICENSE_START=======================================================
# Copyright (c) 2017-2018 AT&T Intellectual Property. All rights reserved.
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

"""mock of cloudify context with relationships and type_hierrarchy"""

from cloudify.mocks import MockCloudifyContext, MockNodeInstanceContext, MockNodeContext

TARGET_NODE_ID = "target_node_id"
TARGET_NODE_NAME = "target_node_name"

class MockContextNode(MockNodeContext):
    """ctx.node with type and type_hierarchy"""

    def __init__(self, id=None, properties=None, node_type=None, type_hierarchy=None):
        super(MockContextNode, self).__init__(id, properties or {})
        self._type = node_type
        self._type_hierarchy = type_hierarchy or [self._type]
        MockCloudifyContextFull.nodes[id] = self

    @property
    def type(self):
        """node type"""
        return self._type

    @property
    def type_hierarchy(self):
        """node type hierarchy is a list of types"""
        return self._type_hierarchy

class MockContextNodeInstance(MockNodeInstanceContext):
    """ctx.instance with relationships"""

    def __init__(self, id=None, runtime_properties=None, relationships=None):
        super(MockContextNodeInstance, self).__init__(id, runtime_properties or {})
        self._relationships = []
        self.add_relationships(relationships)
        MockCloudifyContextFull.instances[id] = self

    def add_relationships(self, relationships):
        """add more relationships to the node instance"""
        if not relationships:
            return
        if not self._relationships:
            self._relationships = []
        self._relationships.extend([
            MockContextRelationship(relationship)
            for relationship in (relationships or []) if TARGET_NODE_ID in relationship
        ])

    @property
    def relationships(self):
        """list of relationships to other node instances"""
        return self._relationships

class MockContextRelationshipTarget(object):
    """target of relationship"""
    def __init__(self, relationship):
        target_node_name = relationship[TARGET_NODE_NAME]
        target_node_id = relationship[TARGET_NODE_ID]

        self.node = MockCloudifyContextFull.nodes.get(target_node_name)
        self.instance = MockCloudifyContextFull.instances.get(target_node_id)

        if not self.node:
            self.node = MockContextNode(target_node_name)
        if not self.instance:
            self.instance = MockContextNodeInstance(target_node_id)

class MockContextRelationship(object):
    """item of ctx.instance.relationships"""

    def __init__(self, relationship):
        self.target = MockContextRelationshipTarget(relationship)
        self.type = relationship.get("type", "cloudify.relationships.depends_on")
        self.type_hierarchy = relationship.get("type_hierarchy") or [self.type]

class MockCloudifyContextFull(MockCloudifyContext):
    """
    ctx1 = MockCloudifyContextFull(node_id='node_1',
                                   node_name='my_1', properties={'foo': 'bar'})
    ctx2 = MockCloudifyContextFull(node_id='node_2',
                                   node_name='my_2',
                                   relationships=[{'target_node_id': 'node_1',
                                                   'target_node_name': 'my_1'}])
    """
    nodes = {}
    instances = {}

    def __init__(self,
                 node_id=None,
                 node_name=None,
                 blueprint_id=None,
                 deployment_id=None,
                 execution_id=None,
                 properties=None, node_type=None, type_hierarchy=None,
                 runtime_properties=None,
                 capabilities=None,
                 related=None,
                 source=None,
                 target=None,
                 operation=None,
                 resources=None,
                 provider_context=None,
                 bootstrap_context=None,
                 relationships=None):
        super(MockCloudifyContextFull, self).__init__(
            node_id=node_id,
            node_name=node_name,
            blueprint_id=blueprint_id,
            deployment_id=deployment_id,
            execution_id=execution_id,
            properties=properties,
            capabilities=capabilities,
            related=related,
            source=source,
            target=target,
            operation=operation,
            resources=resources,
            provider_context=provider_context,
            bootstrap_context=bootstrap_context,
            runtime_properties=runtime_properties
        )
        self._node = MockContextNode(node_name, properties, node_type, type_hierarchy)
        self._instance = MockContextNodeInstance(node_id, runtime_properties, relationships)

    @staticmethod
    def clear():
        """clean up the context links"""
        MockCloudifyContextFull.instances.clear()
        MockCloudifyContextFull.nodes.clear()
