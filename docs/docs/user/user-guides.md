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
# .acme-portal-sdk/flow_finder.py
from typing import List
from acme_portal_sdk.flow_finder import FlowFinder, FlowDetails

class CustomFlowFinder(FlowFinder):
    
    def find_flows(self) -> List[FlowDetails]:
        flows = []
        
        flows.append(FlowDetails(
            name="data_ingestion",
            original_name="data-ingestion",
            description="Daily data ingestion pipeline",
            id="flow_001",
            source_path="/src/pipelines/ingestion.py",
            source_relative="pipelines/ingestion.py",
            grouping=["data", "batch"],
            child_attributes={
                "obj_name": "run_data_ingestion",
                "module": "pipelines.ingestion",
                "import_path": "pipelines.ingestion",
                "priority": 10,
                "category": "critical",
            }
        ))
        
        flows.append(FlowDetails(
            name="data_transformation",
            original_name="data-transformation",
            description="Transform raw data into analytics format",
            id="flow_002",
            source_path="/src/pipelines/transform.py",
            source_relative="pipelines/transform.py",
            grouping=["data", "processing"],
            child_attributes={
                "obj_name": "transform_data",
                "module": "pipelines.transform", 
                "import_path": "pipelines.transform",
                "priority": 5,
                "category": "standard",
            }
        ))
        
        return flows

flow_finder = CustomFlowFinder()
```

Store implementation-specific attributes like `obj_name`, `module`, `import_path` in `child_attributes`.

### Custom DeploymentFinder Implementation

```python
# .acme-portal-sdk/deployment_finder.py
from typing import List
from acme_portal_sdk.deployment_finder import DeploymentFinder, DeploymentDetails

class CustomDeploymentFinder(DeploymentFinder):
    
    def get_deployments(self, project_name: str, branch_name: str, env: str) -> List[DeploymentDetails]:
        deployments = []
        
        deployments.append(DeploymentDetails(
            name=f"{project_name}--{branch_name}--data_ingestion--{env}",
            project_name=project_name,
            branch=branch_name,
            flow_name="data_ingestion",
            env=env,
            commit_hash="abc123def456",
            package_version="1.2.3",
            tags=["production", "critical"],
            id="deploy_001",
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-15T14:20:00Z",
            flow_id="flow_001",
            url="https://deployment-system.com/deployments/deploy_001",
            child_attributes={
                "region": "us-west-2",
                "cpu_limit": "4000m",
                "memory_limit": "8Gi",
                "health_check_enabled": True,
            }
        ))
        
        if env == "dev":
            deployments.append(DeploymentDetails(
                name=f"{project_name}--{branch_name}--data_transformation--{env}",
                project_name=project_name,
                branch=branch_name,
                flow_name="data_transformation",
                env=env,
                commit_hash="def456ghi789",
                package_version="1.2.4-dev",
                tags=["development", "testing"],
                id="deploy_002",
                created_at="2024-01-16T08:15:00Z",
                updated_at="2024-01-16T09:45:00Z",
                flow_id="flow_002",
                url="https://deployment-system.com/deployments/deploy_002",
                child_attributes={
                    "region": "us-east-1",
                    "cpu_limit": "1000m",
                    "memory_limit": "2Gi",
                    "health_check_enabled": False,
                }
            ))
        
        return deployments

deployment_finder = CustomDeploymentFinder()
```

### Custom DeployWorkflow Implementation

[`DeployWorkflow`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow) and [`PromoteWorkflow`](../developer/api-reference.md#acme_portal_sdk.deployment_promote.PromoteWorkflow) use flexible signatures (`*args, **kwargs`) for custom parameters.

```python
# .acme-portal-sdk/flow_deploy.py
from typing import Optional, Dict, Any, List
from acme_portal_sdk.flow_deploy import DeployWorkflow

class CustomDeployWorkflow(DeployWorkflow):
    
    def __init__(self, notification_webhook: Optional[str] = None):
        self.notification_webhook = notification_webhook
    
    def run(self, *args, **kwargs) -> Optional[str]:
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        ref = kwargs.get('ref', args[1] if len(args) > 1 else 'main')
        
        environment = kwargs.get('environment', 'dev')
        config = kwargs.get('deployment_config', {})
        dry_run = kwargs.get('dry_run', False)
        notification_channels = kwargs.get('notification_channels', [])
        
        deployment_id = f"deploy_{hash(f'{flows}_{ref}_{environment}')}"
        
        print(f"Starting deployment {deployment_id}")
        print(f"  Flows: {flows}")
        print(f"  Reference: {ref}")
        print(f"  Environment: {environment}")
        
        if dry_run:
            return f"dry_run_{deployment_id}"
        
        if environment == "prod":
            self._validate_production_deployment(flows, config)
        
        if notification_channels:
            self._send_notifications(notification_channels, deployment_id, flows, environment)
        
        return deployment_id
    
    def _validate_production_deployment(self, flows: List[str], config: Dict[str, Any]):
        required_config = ["resource_limits", "health_checks", "rollback_strategy"]
        missing = [key for key in required_config if key not in config]
        if missing:
            raise ValueError(f"Production deployment requires: {missing}")
    
    def _send_notifications(self, channels: List[str], deployment_id: str, flows: List[str], environment: str):
        message = f"Deployment {deployment_id} completed for flows {flows} in {environment}"
        for channel in channels:
            print(f"  Notification sent to {channel}: {message}")

deploy = CustomDeployWorkflow(notification_webhook="https://hooks.slack.com/...")
```

### Custom PromoteWorkflow Implementation

```python
# .acme-portal-sdk/deployment_promote.py
from typing import Optional, List, Dict, Any
from acme_portal_sdk.deployment_promote import PromoteWorkflow

class CustomPromoteWorkflow(PromoteWorkflow):
    
    def __init__(self, require_approval: bool = True):
        self.require_approval = require_approval
    
    def run(self, *args, **kwargs) -> Optional[str]:
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        source_env = kwargs.get('source_env', args[1] if len(args) > 1 else 'dev')
        target_env = kwargs.get('target_env', args[2] if len(args) > 2 else 'prod')
        ref = kwargs.get('ref', args[3] if len(args) > 3 else 'main')
        
        project_name = kwargs.get('project_name', 'default-project')
        branch_name = kwargs.get('branch_name', 'main')
        auto_approve = kwargs.get('auto_approve', False)
        validation_rules = kwargs.get('validation_rules', [])
        
        promotion_id = f"promote_{hash(f'{flows}_{source_env}_{target_env}_{ref}')}"
        
        print(f"Starting promotion {promotion_id}")
        print(f"  Flows: {flows}")
        print(f"  Source Environment: {source_env}")
        print(f"  Target Environment: {target_env}")
        
        if validation_rules:
            for rule in validation_rules:
                self._run_validation_rule(rule, flows, source_env, target_env)
        
        if self.require_approval and not auto_approve:
            approval_status = self._request_approval(promotion_id, flows, source_env, target_env)
            if not approval_status:
                return None
        
        source_config = self._get_source_deployment_config(flows, source_env)
        target_config = self._apply_target_environment_settings(source_config, target_env)
        
        for flow in flows:
            print(f"    Creating deployment for {flow} in {target_env}")
        
        return promotion_id
    
    def _run_validation_rule(self, rule: str, flows: List[str], source_env: str, target_env: str):
        print(f"    Validating rule: {rule}")
    
    def _request_approval(self, promotion_id: str, flows: List[str], source_env: str, target_env: str) -> bool:
        print(f"    Approval requested for promotion from {source_env} to {target_env}")
        return True
    
    def _get_source_deployment_config(self, flows: List[str], source_env: str) -> Dict[str, Any]:
        return {
            "version": "1.2.3",
            "commit_hash": "abc123def456",
            "resource_limits": {"cpu": "1000m", "memory": "2Gi"},
        }
    
    def _apply_target_environment_settings(self, source_config: Dict[str, Any], target_env: str) -> Dict[str, Any]:
        config = source_config.copy()
        if target_env == "prod":
            config["resource_limits"]["cpu"] = "4000m"
            config["resource_limits"]["memory"] = "8Gi"
        return config

promote = CustomPromoteWorkflow(require_approval=True)
```

### Usage Examples

```python
# Basic usage
deploy_workflow.run(["flow1", "flow2"], "main")
promote_workflow.run(["flow1"], "dev", "prod", "main")

# Extended usage with custom parameters
deploy_workflow.run(
    flows_to_deploy=["data_ingestion", "data_transformation"],
    ref="main",
    environment="staging",
    deployment_config={
        "resource_limits": {"cpu": "2000m", "memory": "4Gi"},
        "health_checks": {"enabled": True, "timeout": 30},
    },
    notification_channels=["slack", "email"]
)

promote_workflow.run(
    flows_to_deploy=["data_ingestion"],
    source_env="staging",
    target_env="prod",
    ref="v1.2.3",
    auto_approve=False,
    validation_rules=["security_scan", "performance_test"]
)
```

## Using GitHub Workflows for Deployment and Promotion

See the [GitHub Workflows Guide](github-workflows.md) for using GitHub Actions as a provider for `DeployWorkflow` and `PromoteWorkflow`.