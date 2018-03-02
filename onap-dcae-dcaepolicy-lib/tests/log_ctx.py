# ================================================================================
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

""":@CtxLogger.log_ctx: decorator for logging the cloudify ctx before and after operation"""

import json
import traceback
from functools import wraps

from cloudify import ctx
from cloudify.context import NODE_INSTANCE, RELATIONSHIP_INSTANCE

class CtxLogger(object):
    """static class for logging cloudify context ctx"""
    @staticmethod
    def _get_ctx_node_info(ctx_node):
        if not ctx_node:
            return {}
        return {'id': ctx_node.id, 'name': ctx_node.name, 'type': ctx_node.type,
                'type_hierarchy': ctx_node.type_hierarchy, 'properties': ctx_node.properties}

    @staticmethod
    def _get_ctx_instance_info(ctx_instance):
        if not ctx_instance:
            return {}
        return {'id' : ctx_instance.id, 'runtime_properties' : ctx_instance.runtime_properties,
                'relationships' : CtxLogger._get_ctx_instance_relationships_info(ctx_instance)}

    @staticmethod
    def _get_ctx_instance_relationships_info(ctx_instance):
        if not ctx_instance or not ctx_instance.relationships:
            return []
        return [{'target': CtxLogger._get_ctx_source_target_info(r.target), \
                 'type':r.type, 'type_hierarchy':r.type_hierarchy} \
                for r in ctx_instance.relationships]

    @staticmethod
    def _get_ctx_source_target_info(ctx_source_target):
        if not ctx_source_target:
            return {}
        return {'node': CtxLogger._get_ctx_node_info(ctx_source_target.node),
                'instance' : CtxLogger._get_ctx_instance_info(ctx_source_target.instance)}

    @staticmethod
    def get_ctx_info():
        """collect the context data from ctx"""
        context = {
            'type': ctx.type,
            'blueprint.id': ctx.blueprint.id,
            'deployment.id': ctx.deployment.id,
            'execution_id': ctx.execution_id,
            'workflow_id': ctx.workflow_id,
            'task_id': ctx.task_id,
            'task_name': ctx.task_name,
            'task_queue': ctx.task_queue,
            'task_target': ctx.task_target,
            'operation': {
                'name': ctx.operation.name,
                'retry_number': ctx.operation.retry_number,
                'max_retries': ctx.operation.max_retries
            },
            'plugin': {
                'name': ctx.plugin.name,
                'package_name': ctx.plugin.package_name,
                'package_version': ctx.plugin.package_version,
                'prefix': ctx.plugin.prefix,
                'workdir': ctx.plugin.workdir
            }
        }
        if ctx.type == NODE_INSTANCE:
            context['node'] = CtxLogger._get_ctx_node_info(ctx.node)
            context['instance'] = CtxLogger._get_ctx_instance_info(ctx.instance)
        elif ctx.type == RELATIONSHIP_INSTANCE:
            context['source'] = CtxLogger._get_ctx_source_target_info(ctx.source)
            context['target'] = CtxLogger._get_ctx_source_target_info(ctx.target)

        return context

    @staticmethod
    def log_ctx_info(func_name):
        """shortcut for logging of the ctx of the function"""
        try:
            if ctx.type == NODE_INSTANCE:
                ctx.logger.info("{0} {1} context: {2}".format(\
                    func_name, ctx.instance.id, json.dumps(CtxLogger.get_ctx_info())))
            elif ctx.type == RELATIONSHIP_INSTANCE:
                ctx.logger.info("{0} context: {1}".format(\
                    func_name, json.dumps(CtxLogger.get_ctx_info())))
        except Exception as ex:
            ctx.logger.error("Failed to log the node context: {0}: {1}" \
                .format(str(ex), traceback.format_exc()))

    @staticmethod
    def log_ctx(pre_log=True, after_log=False, exe_task=None):
        """Decorate each operation on the node to log the context - before and after.
        Optionally save the current function name into runtime_properties[exe_task]
        """
        def log_ctx_info_decorator(func, **arguments):
            """Decorate each operation on the node to log the context"""
            if func is not None:
                @wraps(func)
                def wrapper(*args, **kwargs):
                    """the actual logger before and after"""
                    try:
                        if ctx.type == NODE_INSTANCE and exe_task:
                            ctx.instance.runtime_properties[exe_task] = func.__name__
                    except Exception as ex:
                        ctx.logger.error("Failed to set exe_task {0}: {1}: {2}" \
                            .format(exe_task, str(ex), traceback.format_exc()))
                    if pre_log:
                        CtxLogger.log_ctx_info('before ' + func.__name__)

                    result = func(*args, **kwargs)

                    if after_log:
                        CtxLogger.log_ctx_info('after ' + func.__name__)

                    return result
                return wrapper
        return log_ctx_info_decorator
