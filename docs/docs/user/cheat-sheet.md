# Cheat Sheet

Quick reference for common acme-portal-sdk tasks and commands.

## Common Commands

### CLI Commands

```bash
# Get help
aps --help

# Deploy using prefect
aps-prefect-deploy deploy --help

# Promote deployment
aps-prefect-deploy promote --help

# Copy GitHub workflows
aps github-copy
```

### Configuration Files

#### `.acme_portal_sdk/flow_finder.py`
```python
from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder
from pathlib import Path

project_root = Path(__file__).parent.parent
flow_finder = PrefectFlowFinder(
    root_dir=str(project_root / "src" / "your_project_name")
)
```

#### `.acme_portal_sdk/deployment_finder.py`
```python
from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

deployment_finder = PrefectDeploymentFinder()
```

#### `.acme_portal_sdk/flow_deploy.py`
```python
from acme_portal_sdk.github.github_workflow import GithubActionsDeployWorkflow

deploy = GithubActionsDeployWorkflow(workflow_file="deploy.yml")
```

#### `.acme_portal_sdk/deployment_promote.py`
```python
from acme_portal_sdk.github.github_workflow import GithubActionsPromoteWorkflow

promote = GithubActionsPromoteWorkflow(workflow_file="promote.yml")
```

## Common Patterns

### Flow Configuration
```yaml
# static_flow_deploy_config.yaml
hello_world:
    name: hello_world
    import_path: your_project.flows.hello_world:hello_world
    cron: "0 12 * * 1-5"
    description: Hello World Flow
    work_pool_name: ecs-pool
```

### Environment Setup
```bash
# Set up authentication
prefect cloud login

# Set environment variables
export PREFECT_API_KEY="your-api-key"
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/your-account/workspaces/your-workspace"
```

## Troubleshooting

### Common Issues

1. **Module not found**: Ensure the SDK is installed in your environment
2. **Authentication errors**: Run `prefect cloud login` or set API credentials
3. **GitHub workflow failures**: Check environment secrets are configured

### Debug Commands

```bash
# Check prefect connection
prefect profile ls

# Validate flow configuration
python -c "from .acme_portal_sdk.flow_finder import *"

# Test deployment configuration
aps-prefect-deploy deploy --dry-run
```