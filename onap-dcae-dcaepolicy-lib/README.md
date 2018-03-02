# onap-dcae-dcaepolicy-lib - policy in dcae controller

- python-package to be used in cloudify plugins to maintain the policies lifecycle

## upload the python package to pypi server

```bash
python setup.py sdist upload
```

---

## usage in plugins

### **requirements.txt**

```python
onap-dcae-dcaepolicy-lib==1.0.0
```

### **tasks.py**

import

```python
from onap_dcae_dcaepolicy_lib import Policies
```

### examples of **@operation** with **@Policies.<>** decorator

### Usage:

import the dcaepolicy-node-type.yaml into your blueprint to use the dcae.nodes.type node

```yaml
imports:
    - https://YOUR_NEXUS_RAW_SERVER/type_files/dcaepolicy/1.0.0/node-type.yaml
```

provide the value for policy_id property

```yaml
node_templates:
...
  host_capacity_policy:
    type: dcae.nodes.policy
    properties:
        policy_id: { get_input: host_capacity_policy_id }
```

Then the dcaepolicyplugin will bring the latest policy to the dcae.nodes.policy node during the install workflow of cloudify.

---

### cloudify.interfaces.lifecycle.**configure**

- gather policy data into runtime_properties of policy consumer node

```yaml
cloudify.interfaces.lifecycle:
    configure:
        implementation: dcae_policy_plugin.onap_dcae_dcaepolicy_lib.node_configure
```

```python
from onap_dcae_dcaepolicy_lib import Policies, POLICIES
from .discovery import DiscoveryClient
from .demo_app import DemoApp

APPLICATION_CONFIG = "application_config"
SERVICE_COMPONENT_NAME = "service_component_name"

@operation
@Policies.gather_policies_to_node()
def node_configure(**kwargs):
    """decorate with @Policies.gather_policies_to_node() on policy consumer node to
    prepopulate runtime_properties[POLICIES]
    """
    app_config = ctx.node.properties.get(APPLICATION_CONFIG)

    ctx.instance.runtime_properties[APPLICATION_CONFIG] = app_config
    ctx.logger.info("app_config: {0}".format(json.dumps(app_config)))

    if SERVICE_COMPONENT_NAME in ctx.instance.runtime_properties:
        ctx.logger.info("saving app_config({0}) to consul under key={1}" \
            .format(json.dumps(app_config), \
            ctx.instance.runtime_properties[SERVICE_COMPONENT_NAME]))
        DiscoveryClient.put_kv(ctx.instance.runtime_properties[SERVICE_COMPONENT_NAME], app_config)

    ctx.logger.info("deploying the demo component: {0}...".format(ctx.node.id))
    demo_app = DemoApp(ctx.node.id)
    demo_app.start()
    ctx.logger.info("deployed the demo component: {0}".format(demo_app.container_id))
    demo_app.get_logs()
```

---

### execute-operation **policy-update**

```yaml
dcae.interfaces.policy:
    policy_update:
        implementation: dcae_policy_plugin.onap_dcae_dcaepolicy_lib.policy_update
```

execute-operation **policy-update** that gets a list of changed policy-configs

```python

from .discovery import DiscoveryClient
from .demo_app import DemoApp

APPLICATION_CONFIG = "application_config"
SERVICE_COMPONENT_NAME = "service_component_name"

@operation
@Policies.update_policies_on_node()
def policy_update(updated_policies, removed_policies=None, policies=None, **kwargs):
    """decorate with @Policies.update_policies_on_node() to update runtime_properties[POLICIES]

    :updated_policies: contains the list of changed policy-configs when configs_only=True (default).
    Use configs_only=False to bring the full policy objects in :updated_policies:.
    """
    # example how to notify the dockerized component about the policy change
    notify_app_through_script = True
    if notify_app_through_script:
        ctx.logger.info("notify dockerized app about updated_policies {0} and app_config {1}"
                        .format(json.dumps(updated_policies), json.dumps(app_config)))
        demo_app = DemoApp(ctx.node.id)
        demo_app.notify_app_through_script(
            "policies",
            updated_policies=updated_policies,
            removed_policies=removed_policies,
            policies=policies
        )
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