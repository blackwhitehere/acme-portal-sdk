# Prefect Support

The acme-portal-sdk provides built-in support for Prefect as the primary flow orchestration platform.

## Using default Prefect based functionality

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

[`PrefectDeploymentFinder`](../developer/api-reference.md#acme_portal_sdk.prefect.deployment_finder.PrefectDeploymentFinder) will require prefect client to be authenticated against prefect server like Prefect Cloud before use. You can do this by running `prefect cloud login` and completing the auth process when running locally. For running in CI pipeline you'd need to define `PREFECT_API_KEY` and `PREFECT_API_URL`. Consult prefect [documentation](https://docs.prefect.io/v3/api-ref/rest-api) for how to define it.

```python
# .acme-portal-sdk/deployment_finder.py
from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

deployment_finder = PrefectDeploymentFinder()
```

### `flow_deploy.py`

Relies on using GitHub Actions workflow `.github/workflows/deploy.yml`. You will need to create your own workflow files based on your project's requirements.

View the [example workflow files](https://github.com/blackwhitehere/acme-prefect/tree/main/.github/workflows) in the `acme-prefect` repository's `.github/workflows/` directory for guidance on how to adapt your project including:

* Creating `deploy-prefect` GitHub Environment to hold GitHub `secrets` for connecting to AWS (`acme-config` backend) and Prefect Cloud (`prefect` server).
* Modifying any default triggers for the workflow
* Specifying conatiner image registry (`ghcr.io` by default)
* Modifying default image and package name
* Modifying logic to establish `IMAGE_URI` created in a seperate image build job
* Using [`acme-config`](https://github.com/blackwhitehere/acme-config) to pull environment variables to be used in the deployment
* Using `aps-prefect-deploy` command that relies on static config file read by [`PrefectDeployInfoPrep`](../developer/api-reference.md#acme_portal_sdk.prefect.flow_deploy.PrefectDeployInfoPrep) to specify per flow deployment config.

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

Will be read by [`PrefectDeployInfoPrep`](../developer/api-reference.md#acme_portal_sdk.prefect.flow_deploy.PrefectDeployInfoPrep) used by `aps-prefect-deploy` command that is called from `deploy.yml` and `promote.yml` via `aps-prefect-deploy` call. It allows to define static deployment configuration that varies by deployed flow.

```yaml
hello_world:
    name: hello_world
    import_path: acme_prefect.flows.hello_world:hello_world
    cron: "0 12 * * 1-5"
    description: Hello World
    work_pool_name: ecs-pool
```

## Default functionality of `prefect` based implementation

Prefect based implementation has been designed for a project where a team implements multiple flows that run in a shared python environment, but want to deploy them independently.

* A standard code structure is assumed where flows are defined using the `@flow` decorator across files spread out from a source root.
* Flow names are standardized to use underscores rather than hyphens to align with expectation since flow names are often derived from python function names.
* Deployment name will be composed of a pattern `{project_name}--{branch_name}--{hyphen_flow_name}--{env}` and available to the deployed flow as an env var `DEPLOYMENT_NAME`. This should be used to make sure any persisted data is annotated with label information.
* Versioning info (`PACKAGE_VERSION` and `COMMIT_HASH`) of code used in deployment will be attached as tags to the deployment.
* `Deploy` action is implemented as a GitHub Actions Workflow under `.github/workflows/deploy.yml`. It's triggered automatically on merge to `main` branch following completion of `test.yml` and `container.yml` pipelines that run unit tests and build container image respectively. It uses [`acme-config`](https://github.com/blackwhitehere/acme-config) to retreive current set of environment variables associated with a given environment name. Then, it calls a script `aps-prefect-deploy` that that uses SDK classes (`PrefectDeployInfoPrep`, `PrefectFlowDeployer`) to perform the deployment.
* `Promote` action will extract code version used in source deployment from attached tags and set it to be used in target deployment. It will also set env vars associated with target environment in the new deployment. This way only necessary deployment elements are changed from the source deployment and every other deployment configuration which was tested in source environment is inherited in target environment. It is implemented in `promote.yml` GitHub Action.

## Built-in CLI for prefect based deployment

`acme-portal-sdk` ships with a built in CLI command `aps-prefect-deploy` that implements `deploy` and `promote` commands using SDK classes.

Specifically `PrefectDeployInfoPrep` is used to load a static config file of deployment related configuration and use it as part of deployment information. `PrefectFlowDeployer` is also used to execute the deployment.

For more info run:

    aps-prefect-deploy --help