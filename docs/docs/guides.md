# User Guides

## Configuring SDK for your project

`acme-portal` `VSCode` extension will look into `.acme_portal_sdk` dot directory in root of your open workspace and look for python files:

* `flow_finder.py`
* `flow_deploy.py`
* `deployment_finder.py`
* `deployment_promote.py`

and attempt to find any child classes of:

* `flow_finder.py` -> `FlowDetails` (optional) and `FlowFinder`
* `flow_deploy.py` -> `DeployInfo` (optional) and `DeployWorkflow`
* `deployment_finder.py` -> `DeploymentDetails` (optional) and `DeploymentFinder`
* `deployment_promote.py` -> `PromoteWorkflow`

If optional dataclasses are not defined, the default ones will be assumed to be used.

`acme-portal` will then use other `acme-portal-sdk` internal objects to delegate UI operations performed by the user in `VSCode` extension to appropriate `SDK` class. e.g. using `Deploy` button in UI will trigger a call to `DeployWorkflow.run` method etc.

## Using default `prefect` based functionality

The SDK provides pre-built Prefect implementations you can use with minimal configuration. Below are example code snippets for each required file:

### `flow_finder.py`

```python
# .acme-portal-sdk/flow_finder.py
from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder, PrefectFlowDetails
from pathlib import Path

# Create an instance of PrefectFlowFinder
project_root = Path(__file__).parent.parent
flow_finder = PrefectFlowFinder(
    root_dir=str(project_root / "src" / "your_project_name")
)
```

### `deployment_finder.py`

```python
# .acme-portal-sdk/deployment_finder.py
from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

# Will require prefect client be authenticated against prefect server like prefect cloud
deployment_finder = PrefectDeploymentFinder()
```

### `flow_deploy.py`

Relies on using GitHub Actions workflow `.github/workflows/deploy.yml` which can be copied from `acme_portal_sdk` (alongside `test.yml`, `container.yml` and `promote.yml` pipelines) using command:

    aps github-copy

View `deploy.yml` for details how to adapt your project to it including:

* Specifying conatiner image registry (`ghcr.io` by default)
* Creating `deploy-prefect` GitHub Environment to hold GitHub `secrets` for connecting to AWS (`acme_config` backend) and Prefect Cloud (`prefect` server).
* Using `acme-config` for env var storage
* Using `aps prefect-deploy` command that relies on static config file read by `PrefectDeployInfoPrep`

```python
# .acme-portal-sdk/flow_deploy.py
from acme_portal_sdk.github.github_workflow import GithubActionsDeployWorkflow

deploy = GithubActionsDeployWorkflow(workflow_file="deploy.yml")
```

### `deployment_promote.py`

Is similar to using `deploy.yml` with the same GitHub Environment re-used by this workflow.

```python
# .acme-portal-sdk/deployment_promote.py
from acme_portal_sdk.github.github_workflow import GithubActionsPromoteWorkflow

promote = GithubActionsPromoteWorkflow(workflow_file="promote.yml")
```

### `static_flow_deploy_config.yaml`

Will be read by `PrefectDeployInfoPrep` used by `aps prefect-deploy` command that is called from `deploy.yml` and `promote.yml`. 

```yaml
hello_world:
    name: hello_world
    import_path: acme_prefect.flows.hello_world:hello_world
    cron: "0 12 * * 1-5"
    description: Hello World
    work_pool_name: ecs-pool
```