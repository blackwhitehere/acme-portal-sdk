# acme-portal-sdk

> **Important:** This SDK is currently in alpha and primarily for demonstration purposes. APIs may still change frequently.

## Overview

**acme-portal-sdk** is a Python SDK that provides data and actions for the `acme-portal` VSCode [extension](https://github.com/blackwhitehere/acme-portal). It standardizes the deployment workflow for Python applications that implement "flows" (Jobs/DAGs/Workflows) while allowing full customization of the underlying implementation.

[AI wiki](https://deepwiki.com/blackwhitehere/acme-portal-sdk/)

### Main Idea

Rather than embedding pre-defined deployment logic in the VSCode extension, the SDK allows you to define custom sources of data and behavior. The extension serves as a UI layer to your SDK implementations, providing a consistent interface for:

- **Discovering flows** in your codebase
- **Managing deployments** across environments 
- **Promoting deployments** between environments (dev → staging → prod)

The SDK defines abstract interfaces that you implement according to your project's needs, whether using Prefect, Airflow, GitHub Actions, or custom deployment systems.

## Quick Start

To set up your project with acme-portal-sdk, create a `.acme_portal_sdk` directory in your project root with these files:

### 1. Install the SDK

```bash
pip install acme_portal_sdk
```

### 2. Create SDK Configuration Files

```bash
mkdir .acme_portal_sdk
```

#### `.acme_portal_sdk/flow_finder.py`
```python
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

#### `.acme_portal_sdk/deployment_finder.py`
```python
from acme_portal_sdk.deployment_finder import DeploymentFinder, DeploymentDetails
from typing import List

class MyCustomDeploymentFinder(DeploymentFinder):
    """Custom implementation to find existing deployments."""
    
    def get_deployments(self) -> List[DeploymentDetails]:
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

#### `.acme_portal_sdk/flow_deploy.py`
```python
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

#### `.acme_portal_sdk/deployment_promote.py`
```python
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

### 3. Install VSCode Extension

Install the [`acme-portal` VSCode extension](https://github.com/blackwhitehere/acme-portal) to get the UI interface for managing your flows and deployments.

## Documentation

- **[Core Concepts](docs/docs/user/concepts.md)** - Understanding flows, deployments, and environments
- **[User Guides](docs/docs/user/user-guides.md)** - Detailed configuration examples
- **[Features](docs/docs/user/features.md)** - Available functionality and platform support
- **[API Reference](docs/docs/developer/api-reference.md)** - Complete API documentation

### Example Projects

- **[acme-prefect](https://github.com/blackwhitehere/acme-prefect)** - Complete example using Prefect workflows

## Development

For detailed development setup, contribution guidelines, and release notes process, see [CONTRIBUTING.md](CONTRIBUTING.md).