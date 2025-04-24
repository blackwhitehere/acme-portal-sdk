# User Guides

## Configuring SDK for your project

`acme-portal` `VSCode` extension will look into `.acme_portal_sdk` dot directory in root of your open workspace and look for python files:

* `flow_finder.py`
* `deployment_finder.py`
* `flow_deploy.py`
* `deployment_promote.py`

and attempt to find any child classes of:

* `flow_finder.py` -> `FlowFinder`
* `deployment_finder.py` -> `DeploymentFinder`
* `flow_deploy.py` -> `DeployWorkflow`
* `deployment_promote.py` -> `PromoteWorkflow`

`acme-portal` will then use them to delegate UI operations performed by the user in `VSCode` extension to appropriate `SDK` class. e.g. using `Deploy` button in UI will trigger a call to `DeployWorkflow.run` method etc.

## Using default `prefect` based functionality

You can view a sample project using it under [`acme-prefect`](https://github.com/blackwhitehere/acme-prefect).

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

`PrefectDeploymentFinder` will require prefect client to be authenticated against prefect server like Prefect Cloud before use. You can do this by running `prefect cloud login` and completing the auth process when running locally. For running in CI pipeline you'd need to define PREFECT_API_KEY and PREFECT_API_URL. Consult prefect [documentation](https://docs.prefect.io/v3/api-ref/rest-api) for how to define it.

```python
# .acme-portal-sdk/deployment_finder.py
from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

deployment_finder = PrefectDeploymentFinder()
```

### `flow_deploy.py`

Relies on using GitHub Actions workflow `.github/workflows/deploy.yml` which can be copied from `acme_portal_sdk` (alongside `test.yml`, `container.yml` and `promote.yml` pipelines) to `.github/workflows` directory using command (in root of your project):

    aps github-copy

View `deploy.yml` for details how to adapt your project to it including:

* Specifying conatiner image registry (`ghcr.io` by default)
* Using [`acme-config`](https://github.com/blackwhitehere/acme-config) for env var storage
* Creating `deploy-prefect` GitHub Environment to hold GitHub `secrets` for connecting to AWS (`acme-config` backend) and Prefect Cloud (`prefect` server).
* Using `aps-prefect-deploy` command that relies on static config file read by `PrefectDeployInfoPrep`

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

Will be read by `PrefectDeployInfoPrep` used by `aps-prefect-deploy` command that is called from `deploy.yml` and `promote.yml`. 

```yaml
hello_world:
    name: hello_world
    import_path: acme_prefect.flows.hello_world:hello_world
    cron: "0 12 * * 1-5"
    description: Hello World
    work_pool_name: ecs-pool
```