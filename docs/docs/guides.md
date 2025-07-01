# User Guides

## Configuring SDK for your project

`acme-portal` `VSCode` extension will look into `.acme_portal_sdk` dot directory in root of your open workspace and look for python files:

* `flow_finder.py`
* `deployment_finder.py`
* `flow_deploy.py`
* `deployment_promote.py`

and attempt to find instances of any child classes of:

* `flow_finder.py` -> [`FlowFinder`](api.md#acme_portal_sdk.flow_finder.FlowFinder)
* `deployment_finder.py` -> [`DeploymentFinder`](api.md#acme_portal_sdk.deployment_finder.DeploymentFinder)
* `flow_deploy.py` -> [`DeployWorkflow`](api.md#acme_portal_sdk.flow_deploy.DeployWorkflow)
* `deployment_promote.py` -> [`PromoteWorkflow`](api.md#acme_portal_sdk.deployment_promote.PromoteWorkflow)

`acme-portal` will then use them to delegate UI operations performed by the user in `VSCode` extension to appropriate `SDK` class. e.g. using `Deploy` button in UI will trigger a call to [`DeployWorkflow.run`](api.md#acme_portal_sdk.flow_deploy.DeployWorkflow.run) method etc.

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

[`PrefectDeploymentFinder`](api.md#acme_portal_sdk.prefect.deployment_finder.PrefectDeploymentFinder) will require prefect client to be authenticated against prefect server like Prefect Cloud before use. You can do this by running `prefect cloud login` and completing the auth process when running locally. For running in CI pipeline you'd need to define `PREFECT_API_KEY` and `PREFECT_API_URL`. Consult prefect [documentation](https://docs.prefect.io/v3/api-ref/rest-api) for how to define it.

```python
# .acme-portal-sdk/deployment_finder.py
from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

deployment_finder = PrefectDeploymentFinder()
```

### `flow_deploy.py`

Relies on using GitHub Actions workflow `.github/workflows/deploy.yml` which can be copied from `acme_portal_sdk` (alongside `test.yml`, `container.yml` and `promote.yml` pipelines) to `.github/workflows` directory using command (in root of your project):

    aps github-copy

View `deploy.yml` for details how to adapt your project to it including:

* Creating `deploy-prefect` GitHub Environment to hold GitHub `secrets` for connecting to AWS (`acme-config` backend) and Prefect Cloud (`prefect` server).
* Modifying any default triggers for the workflow
* Specifying conatiner image registry (`ghcr.io` by default)
* Modifying default image and package name
* Modifying logic to establish IMAGE_URI created in a seperate image build job
* Using [`acme-config`](https://github.com/blackwhitehere/acme-config) to pull environment variables to be used in the deployment
* Using `aps-prefect-deploy` command that relies on static config file read by [`PrefectDeployInfoPrep`](api.md#acme_portal_sdk.prefect.flow_deploy.PrefectDeployInfoPrep) to specify per flow deployment config.

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

Will be read by [`PrefectDeployInfoPrep`](api.md#acme_portal_sdk.prefect.flow_deploy.PrefectDeployInfoPrep) used by `aps-prefect-deploy` command that is called from `deploy.yml` and `promote.yml` via `aps-prefect-deploy` call. It allows to define static deployment configuration that varies by deployed flow.

```yaml
hello_world:
    name: hello_world
    import_path: acme_prefect.flows.hello_world:hello_world
    cron: "0 12 * * 1-5"
    description: Hello World
    work_pool_name: ecs-pool
```

## Creating Custom Workflow Implementations

The SDK provides flexible workflow interfaces that allow you to create custom implementations for different deployment and promotion strategies.

### Flexible Workflow Signatures

Both [`DeployWorkflow`](api.md#acme_portal_sdk.flow_deploy.DeployWorkflow) and [`PromoteWorkflow`](api.md#acme_portal_sdk.deployment_promote.PromoteWorkflow) use flexible method signatures with `*args, **kwargs` to support different implementation requirements:

```python
class DeployWorkflow(ABC):
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Run deployment workflow with flexible parameters."""
        pass

class PromoteWorkflow(ABC):
    @abstractmethod  
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Run promotion workflow with flexible parameters."""
        pass
```

This design allows implementations to:
- Accept additional parameters beyond the basic requirements
- Support different deployment patterns and configurations
- Maintain backward compatibility with existing usage
- Enable future extensibility without breaking changes

### Common Parameters

While implementations can accept any parameters, these are commonly used:

**Deploy workflows:**
- `flows_to_deploy`: List of flow names to deploy
- `ref`: Git reference (branch/tag) to deploy
- `project_name`: Name of the project
- `env`: Target environment
- `image_uri`: Docker image URI
- `package_version`: Package version

**Promote workflows:**
- `flows_to_deploy`: List of flow names to promote
- `source_env`: Source environment name
- `target_env`: Target environment name  
- `ref`: Git reference to promote

### Example: Custom Deploy Workflow

```python
from acme_portal_sdk.flow_deploy import DeployWorkflow
from typing import Any, Optional

class CustomDeployWorkflow(DeployWorkflow):
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        # Extract standard parameters
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        ref = kwargs.get('ref', args[1] if len(args) > 1 else 'main')
        
        # Handle custom parameters for your deployment strategy
        environment = kwargs.get('environment', 'dev')
        config = kwargs.get('deployment_config', {})
        webhook = kwargs.get('notification_webhook')
        retry_count = kwargs.get('retry_count', 3)
        
        # Your custom deployment logic
        return self.execute_custom_deployment(
            flows, ref, environment, config, webhook, retry_count
        )
    
    def execute_custom_deployment(self, flows, ref, env, config, webhook, retries):
        # Implement your custom deployment logic here
        # Return URL or identifier of the deployment
        pass
```

### Usage Examples

**Basic usage (backward compatible):**
```python
# These calls work with any implementation
deploy_workflow.run(["flow1", "flow2"], "main")
promote_workflow.run(["flow1"], "dev", "prod", "main")
```

**Extended usage with custom parameters:**
```python
# Deploy with additional configuration
deploy_workflow.run(
    flows_to_deploy=["user-service", "auth-service"],
    ref="feature/new-auth",
    environment="staging",
    deployment_config={"replicas": 3, "memory_limit": "512Mi"},
    notification_webhook="https://hooks.slack.com/webhooks/...",
    retry_count=5
)

# Promote with advanced options
promote_workflow.run(
    flows_to_deploy=["payment-processor"],
    source_env="staging",
    target_env="production",
    ref="release/v2.1.0",
    approval_required=True,
    health_checks=["api-health", "database-connectivity"]
)
```

This flexibility enables you to build workflow implementations that meet your specific deployment requirements while maintaining compatibility with the acme-portal VSCode extension.