# User Guides

## Configuring SDK for your project

Create a `.acme_portal_sdk` directory in your workspace root with these Python files:

* `flow_finder.py` -> [`FlowFinder`](../developer/api-reference.md#acme_portal_sdk.flow_finder.FlowFinder)
* `deployment_finder.py` -> [`DeploymentFinder`](../developer/api-reference.md#acme_portal_sdk.deployment_finder.DeploymentFinder)
* `flow_deploy.py` -> [`DeployWorkflow`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow)
* `deployment_promote.py` -> [`PromoteWorkflow`](../developer/api-reference.md#acme_portal_sdk.deployment_promote.PromoteWorkflow)

The VSCode extension will use these classes to handle UI operations.

## Using platform-specific implementations

* **Prefect**: See [Prefect Support](prefect.md)
* **Airflow**: See [Airflow Support](airflow.md)
* **GitHub Workflows**: See [GitHub Workflows Guide](github-workflows.md)

## Creating Custom Workflow Implementations

Extend the base classes to create custom implementations for your specific needs.

### Base Classes

* [`FlowFinder`](../developer/api-reference.md#acme_portal_sdk.flow_finder.FlowFinder) - Discovers flows in your codebase
* [`DeploymentFinder`](../developer/api-reference.md#acme_portal_sdk.deployment_finder.DeploymentFinder) - Finds existing deployments
* [`DeployWorkflow`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow) - Handles flow deployment operations
* [`PromoteWorkflow`](../developer/api-reference.md#acme_portal_sdk.deployment_promote.PromoteWorkflow) - Manages deployment promotion between environments

### Custom FlowFinder Implementation

```python
# .acme_portal_sdk/flow_finder.py
from acme_portal_sdk.flow_finder import FlowFinder, FlowDetails
from typing import List

class MyCustomFlowFinder(FlowFinder):
    """Custom implementation to find flows in your codebase."""
    
    def find_flows(self) -> List[FlowDetails]:
        """Return sample flows."""
        return [
            FlowDetails(
                name="data_processing_flow",
                original_name="data_processing_flow",
                description="Processes daily data files",
                id="flows.data_processing_flow",
                source_path="/src/flows/data_processing.py",
                source_relative="flows/data_processing.py",
                line_number=15,
                grouping=["data"],
                child_attributes={"schedule": "daily"}
            ),
            FlowDetails(
                name="report_generation_flow", 
                original_name="report_generation_flow",
                description="Generates weekly reports",
                id="flows.report_generation_flow",
                source_path="/src/flows/reports.py",
                source_relative="flows/reports.py",
                line_number=25,
                grouping=["reports"]
            )
        ]

flow_finder = MyCustomFlowFinder()
```

### Custom DeploymentFinder Implementation

```python
# .acme_portal_sdk/deployment_finder.py
from acme_portal_sdk.deployment_finder import DeploymentFinder, DeploymentDetails
from acme_portal_sdk.flow_finder import FlowDetails
from typing import List, Optional

class MyCustomDeploymentFinder(DeploymentFinder):
    """Custom implementation to find existing deployments."""
    
    def get_deployments(
        self,
        *,
        deployments_to_fetch: Optional[List[DeploymentDetails]] = None,
        flows_to_fetch: Optional[List[FlowDetails]] = None,
    ) -> List[DeploymentDetails]:
        """Return sample deployments."""
        return [
            DeploymentDetails(
                name="data-processing-prod",
                project_name="my-project",
                branch="main",
                flow_name="data_processing_flow",
                env="prod",
                commit_hash="abc123def456",
                package_version="1.2.3",
                tags=["production", "daily"],
                id="deploy-001",
                created_at="2024-01-15T10:00:00Z",
                updated_at="2024-01-15T10:00:00Z",
                flow_id="flows.data_processing_flow",
                url="https://deployment-system.com/deploy-001",
                child_attributes={"replicas": 3}
            ),
            DeploymentDetails(
                name="reports-staging",
                project_name="my-project", 
                branch="develop",
                flow_name="report_generation_flow",
                env="staging",
                commit_hash="def456ghi789",
                package_version="1.3.0-dev",
                tags=["staging", "weekly"],
                id="deploy-002",
                created_at="2024-01-16T14:30:00Z",
                updated_at="2024-01-16T14:30:00Z",
                flow_id="flows.report_generation_flow",
                url="https://deployment-system.com/deploy-002"
            )
        ]

deployment_finder = MyCustomDeploymentFinder()
```

### Custom DeployWorkflow Implementation

```python
# .acme_portal_sdk/flow_deploy.py
from acme_portal_sdk.flow_deploy import DeployWorkflow
from typing import Any, Optional

class MyCustomDeployWorkflow(DeployWorkflow):
    """Custom implementation for deploying flows."""
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Return sample deployment URL."""
        flows_to_deploy = kwargs.get("flows_to_deploy", [])
        env = kwargs.get("env", "dev")
        
        # Return sample deployment URL 
        return f"https://deployment-system.com/deployments/{env}-{len(flows_to_deploy)}-flows"

deploy = MyCustomDeployWorkflow()
```

### Custom PromoteWorkflow Implementation

```python
# .acme_portal_sdk/deployment_promote.py
from acme_portal_sdk.deployment_promote import PromoteWorkflow
from typing import Any, Optional

class MyCustomPromoteWorkflow(PromoteWorkflow):
    """Custom implementation for promoting deployments between environments."""
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Return sample promotion URL."""
        flows_to_deploy = kwargs.get("flows_to_deploy", [])
        source_env = kwargs.get("source_env", "dev")
        target_env = kwargs.get("target_env", "prod")
        
        # Return sample promotion URL
        return f"https://deployment-system.com/promotions/{source_env}-to-{target_env}-{len(flows_to_deploy)}-flows"

promote = MyCustomPromoteWorkflow()
```



## Using GitHub Workflows for Deployment and Promotion

See the [GitHub Workflows Guide](github-workflows.md) for using GitHub Actions as a provider for `DeployWorkflow` and `PromoteWorkflow`.