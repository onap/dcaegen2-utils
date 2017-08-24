# dcaepolicy - policy in dcae controller
- python-package to be used in cloudify plugins to maintain the policies lifecycle

## [setup pypi connection](./nexus_pypi.md) to **nexus** repo server

## build = register and upload to nexus repo server

```bash
./dev_run.sh build
```

## upload the python package to nexus repo server

```bash
./dev_run.sh upload
```

---
# usage in plugins

**requirements.txt**
```python
--extra-index-url https://YOUR_NEXUS_PYPI_SERVER/simple
dcaepolicy
```

**tasks.py**
- import

```python
from dcaepolicy import Policies
```

# examples of **@operation** with **@Policies.<>** decorator

## **dcae.nodes.policy** cloudify.interfaces.lifecycle.**create**

- retrieve the latest policy data on dcae.nodes.policy node 
```yaml
    dcae.nodes.policy:
        derived_from: cloudify.nodes.Root
        properties:
            policy_id:
                description: PK to policy
                type: string
                default: DCAE_alex.Config_empty-policy
            policy_apply_mode:
                description: choice of how to apply the policy update (none|script)
                type: string
                default: none
        interfaces:
            cloudify.interfaces.lifecycle:
                create:
                    implementation: dcae_policy_plugin.dcaepolicy.policy_get
```

```python
@operation
@Policies.populate_policy_on_node
def policy_get(**kwargs):
    """decorate with @Policies.populate_policy_on_node on dcae.nodes.policy node to
    retrieve the latest policy_body for policy_id
    property and save it in runtime_properties
    """
    pass
```

------
## cloudify.interfaces.lifecycle.**configure**
- gather policy data into runtime_properties of policy consumer node
```yaml
cloudify.interfaces.lifecycle:
    configure:
        implementation: dcae_policy_plugin.dcaepolicy.node_configure

```

```python

from dcaepolicy import Policies, POLICIES
from .discovery import DiscoveryClient
from .demo_app import DemoApp

APPLICATION_CONFIG = "application_config"
SERVICE_COMPONENT_NAME = "service_component_name"

@operation
@Policies.gather_policies_to_node
def node_configure(**kwargs):
    """decorate with @Policies.gather_policies_to_node on policy consumer node to
    prepopulate runtime_properties[POLICIES]
    """
    app_config = None
    if APPLICATION_CONFIG in ctx.node.properties:
        # dockerized blueprint puts the app config into property application_config
        app_config = ctx.node.properties.get(APPLICATION_CONFIG)
    else:
        # CDAP components expect that in property app_config
        app_config = ctx.node.properties.get("app_config")

    app_config = Policies.shallow_merge_policies_into(app_config)
    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config
    ctx.logger.info("example: applied policy_configs to property app_config: {0}" \
        .format(json.dumps(app_config)))

    if SERVICE_COMPONENT_NAME in ctx.instance.runtime_properties:
        ctx.logger.info("saving app_config({0}) to consul under key={1}" \
            .format(json.dumps(app_config), \
            ctx.instance.runtime_properties[SERVICE_COMPONENT_NAME]))
        DiscoveryClient.put_kv(ctx.instance.runtime_properties[SERVICE_COMPONENT_NAME], app_config)

    # alternative 1 - use the list of policy configs from policies in runtime_properties
    policy_configs = Policies.get_policy_configs()
    if policy_configs:
        ctx.logger.warn("TBD: apply policy_configs: {0}".format(json.dumps(policy_configs)))

    # alternative 2 - use the policies dict by policy_id from runtime_properties
    if POLICIES in ctx.instance.runtime_properties:
        policies = ctx.instance.runtime_properties[POLICIES]
        ctx.logger.warn("TBD: apply policies: {0}".format(json.dumps(policies)))

    ctx.logger.info("deploying the demo component: {0}...".format(ctx.node.id))
    demo_app = DemoApp(ctx.node.id)
    demo_app.start()
    ctx.logger.info("deployed the demo component: {0}".format(demo_app.container_id))
    demo_app.get_logs()
```

------
## execute-operation **policy-update**
```yaml
dcae.interfaces.policy:
    policy_update:
        implementation: dcae_policy_plugin.dcaepolicy.policy_update
```

execute-operation **policy-update** that gets a list of changed policy-configs
```python

from .discovery import DiscoveryClient
from .demo_app import DemoApp

APPLICATION_CONFIG = "application_config"
SERVICE_COMPONENT_NAME = "service_component_name"

@operation
@Policies.update_policies_on_node(configs_only=True)
def policy_update(updated_policies, notify_app_through_script=False, **kwargs):
    """decorate with @Policies.update_policies_on_node() to update runtime_properties[POLICIES]

    :updated_policies: contains the list of changed policy-configs when configs_only=True (default).
    Use configs_only=False to bring the full policy objects in :updated_policies:.

    :notify_app_through_script: in kwargs is set to True/False to indicate whether to invoke
    the script based on policy_apply_mode property in the blueprint
    """

    if not updated_policies or POLICIES not in ctx.instance.runtime_properties:
        return

    app_config = DiscoveryClient.get_value(ctx.instance.runtime_properties[SERVICE_COMPONENT_NAME])
    app_config = Policies.shallow_merge_policies_into(app_config)
    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config
    ctx.logger.info("example: updated app_config {0} with updated_policies: {1}" \
        .format(json.dumps(app_config), json.dumps(updated_policies)))
    DiscoveryClient.put_kv(ctx.instance.runtime_properties[SERVICE_COMPONENT_NAME], app_config)

    if notify_app_through_script:
        demo_app = DemoApp(ctx.node.id)
        demo_app.notify_app_through_script(
            POLICY_MESSAGE_TYPE,
            updated_policies=updated_policies,
            application_config=app_config
        )

    # alternative 1 - use the list of updated_policies on your own
    if updated_policies:
        ctx.logger.warn("TBD: apply updated_policies: {0}".format(json.dumps(updated_policies)))
```

example of the **changed\_policies** with **configs_only=True** 
- list of config objects (preparsed from json string) 
- manual mess produced by mock_policy_updater
```json
[{
	"policy_updated_from_ver": "2",
	"policy_updated_to_ver": "3",
	"updated_policy_id": "DCAE_alex.Config_db_client_policy_id_value",
	"policy_hello": "world!",
	"policy_updated_ts": "2017-08-17T21:49:39.279187Z"
}]
```
---

example of **policies** in runtime_properties **before policy-update**

```json
"runtime_properties": {
    "execute_operation": "policy_update",
    "service_component_name": "some-uuid.unknown.unknown.unknown.dcae.ecomp.company.com",
    "application_config": {
        "policy_hello": "world!",
        "db": {
            "type": "db",
            "input_db_port": 5555,
            "database_port": 5555
        },
        "policy_updated_from_ver": "1",
        "intention": "policies are shallow merged to the copy of the application_config",
        "updated_policy_id": "DCAE_alex.Config_db_client_policy_id_value",
        "client": {
            "client_version": "1.2.2",
            "type": "client",
            "client_policy_id": "DCAE_alex.Config_db_client_policy_id_value"
        },
        "policy_updated_ts": "2017-08-17T21:13:47.268782Z",
        "policy_updated_to_ver": "2"
    },
    "exe_task": "node_configure",
    "policies": {
        "DCAE_alex.Config_db_client_policy_id_value": {
            "policy_apply_mode": "script",
            "policy_body": {
                "policyName": "DCAE_alex.Config_db_client_policy_id_value.2.xml",
                "policyConfigMessage": "Config Retrieved! ",
                "responseAttributes": {
                    
                },
                "policyConfigStatus": "CONFIG_RETRIEVED",
                "matchingConditions": {
                    "ECOMPName": "DCAE",
                    "ConfigName": "alex_config_name"
                },
                "type": "OTHER",
                "property": null,
                "config": {
                    "policy_updated_from_ver": "1",
                    "policy_updated_to_ver": "2",
                    "updated_policy_id": "DCAE_alex.Config_db_client_policy_id_value",
                    "policy_hello": "world!",
                    "policy_updated_ts": "2017-08-17T21:13:47.268782Z"
                },
                "policyVersion": "2"
            },
            "policy_id": "DCAE_alex.Config_db_client_policy_id_value"
        }
    }
}
```

example of **policies** in runtime_properties **after policy-update**

```json
"runtime_properties": {
    "execute_operation": "policy_update",
    "service_component_name": "some-uuid.unknown.unknown.unknown.dcae.ecomp.company.com",
    "application_config": {
        "policy_hello": "world!",
        "db": {
            "input_db_port": 5555,
            "type": "db",
            "database_port": 5555
        },
        "policy_updated_ts": "2017-08-17T21:49:39.279187Z",
        "policy_updated_from_ver": "2",
        "intention": "policies are shallow merged to the copy of the application_config",
        "client": {
            "client_version": "1.2.2",
            "type": "client",
            "client_policy_id": "DCAE_alex.Config_db_client_policy_id_value"
        },
        "updated_policy_id": "DCAE_alex.Config_db_client_policy_id_value",
        "policy_updated_to_ver": "3"
    },
    "exe_task": "node_configure",
    "policies": {
        "DCAE_alex.Config_db_client_policy_id_value": {
            "policy_apply_mode": "script",
            "policy_body": {
                "policyName": "DCAE_alex.Config_db_client_policy_id_value.3.xml",
                "policyConfigMessage": "Config Retrieved! ",
                "responseAttributes": {
                    
                },
                "policyConfigStatus": "CONFIG_RETRIEVED",
                "matchingConditions": {
                    "ECOMPName": "DCAE",
                    "ConfigName": "alex_config_name"
                },
                "type": "OTHER",
                "property": null,
                "config": {
                    "policy_updated_from_ver": "2",
                    "policy_updated_to_ver": "3",
                    "updated_policy_id": "DCAE_alex.Config_db_client_policy_id_value",
                    "policy_hello": "world!",
                    "policy_updated_ts": "2017-08-17T21:49:39.279187Z"
                },
                "policyVersion": "3"
            },
            "policy_id": "DCAE_alex.Config_db_client_policy_id_value"
        }
    }
}
```

---