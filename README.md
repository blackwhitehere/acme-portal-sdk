# acme-portal-sdk

> **Important:** This SDK is currently in alpha and primarily for demonstration purposes. APIs may still change frequently.

## Overview

**acme-portal-sdk** is a Python SDK that provides data and actions for the `acme-portal` VSCode [extension](https://github.com/blackwhitehere/acme-portal). It standardizes the deployment workflow for Python applications that implement "flows" (Jobs/DAGs/Workflows) while allowing full customization of the underlying implementation.

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
from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder
from pathlib import Path

# Create an instance to find flows in your project
project_root = Path(__file__).parent.parent
flow_finder = PrefectFlowFinder(
    root_dir=str(project_root / "src" / "your_project_name")
)
```

#### `.acme_portal_sdk/deployment_finder.py`
```python
from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

# Find existing deployments (requires Prefect authentication)
deployment_finder = PrefectDeploymentFinder()
```

#### `.acme_portal_sdk/flow_deploy.py`
```python
from acme_portal_sdk.github.github_workflow import GithubActionsDeployWorkflow

# Deploy flows using GitHub Actions
deploy = GithubActionsDeployWorkflow(workflow_file="deploy.yml")
```

#### `.acme_portal_sdk/deployment_promote.py`
```python
from acme_portal_sdk.github.github_workflow import GithubActionsPromoteWorkflow

# Promote deployments between environments
promote = GithubActionsPromoteWorkflow(workflow_file="promote.yml")
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