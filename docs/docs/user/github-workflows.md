# Using GitHub as a Provider for DeployWorkflow and PromoteWorkflow

This document provides guidance on using GitHub Actions as a provider for implementing the `DeployWorkflow` and `PromoteWorkflow` interfaces in the `acme_portal_sdk`.

## Deploying Flows with `GithubActionsDeployWorkflow`

The `GithubActionsDeployWorkflow` class implements the `DeployWorkflow` interface using GitHub Actions. It allows you to deploy flows by triggering a GitHub Actions workflow.

### Example Usage

```python
from acme_portal_sdk.github.github_workflow import GithubActionsDeployWorkflow

deploy = GithubActionsDeployWorkflow(workflow_file="deploy.yml")

deploy.run(flows_to_deploy=["flow1", "flow2"], ref="main")
```

### Key Features

- **Workflow File**: Specify the GitHub Actions workflow file (default: `deploy.yml`).
- **Git Ref**: Use the `ref` parameter to specify the branch or tag for the workflow.
- **Extensibility**: Accepts additional parameters via `**kwargs` for custom implementations.

## Promoting Flows with `GithubActionsPromoteWorkflow`

The `GithubActionsPromoteWorkflow` class implements the `PromoteWorkflow` interface using GitHub Actions. It facilitates promoting flows between environments (e.g., from `dev` to `prod`).

### Example Usage

```python
from acme_portal_sdk.github.github_workflow import GithubActionsPromoteWorkflow

promote = GithubActionsPromoteWorkflow(workflow_file="promote.yml")

promote.run(flows_to_deploy=["flow1"], source_env="dev", target_env="prod", ref="main")
```

### Key Features

- **Workflow File**: Specify the GitHub Actions workflow file (default: `promote.yml`).
- **Environment Transition**: Define `source_env` and `target_env` for the promotion.
- **Extensibility**: Accepts additional parameters via `**kwargs` for custom implementations.

## Creating Custom Workflow Implementations

Both `DeployWorkflow` and `PromoteWorkflow` use flexible signatures (`*args, **kwargs`) to allow custom implementations to accept additional parameters beyond the standard ones.

### Example Custom Implementation

```python
from acme_portal_sdk.flow_deploy import DeployWorkflow

class CustomDeployWorkflow(DeployWorkflow):
    def run(self, *args, **kwargs):
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        ref = kwargs.get('ref', args[1] if len(args) > 1 else 'main')
        
        # Accept custom parameters
        environment = kwargs.get('environment', 'dev')
        config = kwargs.get('deployment_config', {})
        
        print(f"Deploying flows: {flows} to environment: {environment} using ref: {ref}")
```

## Monitoring Workflows

After triggering a workflow, you can monitor its progress using the URL returned by the `run` method. For example:

```python
run_url = deploy.run(flows_to_deploy=["flow1"], ref="main")
if run_url:
    print(f"Monitor the workflow at: {run_url}")
else:
    print("Failed to trigger the workflow.")
```
