# User Guides

## Configuring SDK for your project

`acme-portal` `VSCode` extension will look into `.acme_portal_sdk` dot directory in root of your open workspace and look for python files:

* `flow_finder.py`
* `deployment_finder.py`
* `flow_deploy.py`
* `deployment_promote.py`

and attempt to find instances of any child classes of:

* `flow_finder.py` -> [`FlowFinder`](../developer/api-reference.md#acme_portal_sdk.flow_finder.FlowFinder)
* `deployment_finder.py` -> [`DeploymentFinder`](../developer/api-reference.md#acme_portal_sdk.deployment_finder.DeploymentFinder)
* `flow_deploy.py` -> [`DeployWorkflow`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow)
* `deployment_promote.py` -> [`PromoteWorkflow`](../developer/api-reference.md#acme_portal_sdk.deployment_promote.PromoteWorkflow)

`acme-portal` will then use them to delegate UI operations performed by the user in `VSCode` extension to appropriate `SDK` class. e.g. using `Deploy` button in UI will trigger a call to [`DeployWorkflow.run`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow.run) method etc.

## Using platform-specific implementations

For specific platform implementations:

* **Prefect**: See the [Prefect Support](prefect.md) documentation for details on using the built-in Prefect implementations
* **Airflow**: See the [Airflow Support](airflow.md) documentation for details on using the built-in Airflow implementations
* **GitHub Workflows**: See the [GitHub Workflows Guide](github-workflows.md) for using GitHub Actions as a deployment provider

## Creating Custom Workflow Implementations

The SDK provides base classes that you can extend to create custom implementations for your specific needs. Each base class can be configured using subclasses that implement sample functionality and return custom data.

### Overview of Base Classes

The SDK defines four main base classes that need to be implemented:

* [`FlowFinder`](../developer/api-reference.md#acme_portal_sdk.flow_finder.FlowFinder) - Discovers flows in your codebase
* [`DeploymentFinder`](../developer/api-reference.md#acme_portal_sdk.deployment_finder.DeploymentFinder) - Finds existing deployments
* [`DeployWorkflow`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow) - Handles flow deployment operations
* [`PromoteWorkflow`](../developer/api-reference.md#acme_portal_sdk.deployment_promote.PromoteWorkflow) - Manages deployment promotion between environments

### Custom FlowFinder Implementation

Create a custom `FlowFinder` subclass to discover flows in your codebase:

```python
# .acme-portal-sdk/flow_finder.py
from typing import List
from acme_portal_sdk.flow_finder import FlowFinder, FlowDetails

class CustomFlowFinder(FlowFinder):
    """Custom flow finder that discovers flows with custom metadata."""
    
    def find_flows(self) -> List[FlowDetails]:
        # Sample implementation that returns flows with custom metadata
        flows = []
        
        # Example: discover critical batch processing flows
        flows.append(FlowDetails(
            name="data_ingestion",
            original_name="data-ingestion",
            description="Daily data ingestion pipeline",
            id="flow_001",
            source_path="/src/pipelines/ingestion.py",
            source_relative="pipelines/ingestion.py",
            grouping=["data", "batch"],
            child_attributes={
                # Implementation-specific attributes go here
                "obj_type": "function",
                "obj_name": "run_data_ingestion",
                "obj_parent_type": "module",
                "obj_parent": "pipelines.ingestion",
                "module": "pipelines.ingestion",
                "import_path": "pipelines.ingestion",
                # Custom metadata for your specific needs
                "priority": 10,  # High priority
                "category": "critical",
            }
        ))
        
        # Example: discover standard processing flows
        flows.append(FlowDetails(
            name="data_transformation",
            original_name="data-transformation",
            description="Transform raw data into analytics format",
            id="flow_002",
            source_path="/src/pipelines/transform.py",
            source_relative="pipelines/transform.py",
            grouping=["data", "processing"],
            child_attributes={
                # Implementation-specific attributes go here
                "obj_type": "function",
                "obj_name": "transform_data",
                "obj_parent_type": "module",
                "obj_parent": "pipelines.transform",
                "module": "pipelines.transform", 
                "import_path": "pipelines.transform",
                # Custom metadata for your specific needs
                "priority": 5,  # Medium priority
                "category": "standard",
            }
        ))
        
        return flows

# Create the instance
flow_finder = CustomFlowFinder()
```

**Important:** The `child_attributes` field should be used to store any custom metadata or implementation-specific attributes like `obj_type`, `obj_name`, etc. Platform implementations like `PrefectFlowFinder` and `AirflowFlowFinder` automatically populate these attributes when discovering flows.

### FlowDetails API Changes in v1.0.0

Version 1.0.0 introduces significant changes to the `FlowDetails` class structure to make it more flexible and implementation-agnostic. This section explains the architectural changes and the reasoning behind them.

#### Architectural Changes

**Before v1.0.0:**
The `FlowDetails` class required several implementation-specific attributes as part of its constructor. This created tight coupling between the base class and specific implementations:

```python
# Old API - implementation details required in base class
FlowDetails(
    name="my_flow",
    obj_type="function",      # Implementation detail
    obj_name="my_function",   # Implementation detail  
    obj_parent_type="module", # Implementation detail
    obj_parent="my_module",   # Implementation detail
    module="my_module",       # Implementation detail
    import_path="my.module",  # Implementation detail
    # ... other required fields
)
```

**After v1.0.0:**
The `FlowDetails` class has been simplified to focus only on essential flow metadata. Implementation-specific details are now stored in the flexible `child_attributes` dictionary:

```python
# New API - implementation details in child_attributes
FlowDetails(
    name="my_flow",
    id="flow_123",
    source_path="/path/to/file.py",
    source_relative="file.py",
    child_attributes={
        "obj_type": "function",      # Implementation detail
        "obj_name": "my_function",   # Implementation detail
        "obj_parent_type": "module", # Implementation detail
        "obj_parent": "my_module",   # Implementation detail
        "module": "my_module",       # Implementation detail
        "import_path": "my.module",  # Implementation detail
    }
)
```

#### Benefits of the New Architecture

1. **Cleaner Base Class**: The base `FlowDetails` class now only requires truly essential attributes that apply to all flow implementations
2. **Implementation Flexibility**: Different platforms (Prefect, Airflow, custom) can store their own specific metadata without affecting the base interface
3. **Future-Proof Design**: New implementations can add their own attributes without requiring changes to the base class
4. **Separation of Concerns**: Core flow identity is separated from implementation-specific metadata

#### Attribute Categories

**Core Required Attributes** (always required):
- `name` - Display name for the flow
- `original_name` - Original name as defined in source code
- `description` - Flow description
- `id` - Unique identifier for the flow
- `source_path` - Absolute path to source file
- `source_relative` - Relative path to source file

**Optional Core Attributes** (may be useful across implementations):
- `grouping` - Logical grouping of flows
- `tags` - Flow tags for categorization

**Implementation-Specific Attributes** (stored in `child_attributes`):
- `obj_type` - Type of object (function, method, class)
- `obj_name` - Name of the implementing object
- `obj_parent_type` - Type of parent container (module, class)
- `obj_parent` - Name of parent container
- `module` - Python module name
- `import_path` - Full import path
- Any platform-specific metadata

#### Impact on Different User Types

**Platform Implementation Users** (using `PrefectFlowFinder`, `AirflowFlowFinder`):
- **No changes required** to your setup code
- Flow discovery continues to work as before
- Access implementation-specific attributes via `flow.child_attributes["attr_name"]`

**Custom Implementation Developers**:
- Update `FlowDetails` creation to use `child_attributes` for implementation-specific data
- Base class constructor is now simpler and more focused
- More flexibility in what metadata to store

**SDK Extenders**:
- Can now store custom metadata in `child_attributes` without conflicts
- No need to subclass `FlowDetails` for most customization needs
- Easier to integrate with different workflow platforms

### Migration Guide for FlowDetails API Changes

Starting with version 1.0.0, the `FlowDetails` class has been simplified to make several attributes optional that were previously required. This is a **breaking change** that affects how you work with FlowDetails objects.

#### What Changed

Previously required attributes that are now in `child_attributes`:
- `obj_type` - Type of object defining the flow (e.g., function, method)
- `obj_name` - Name of the object defining the flow 
- `obj_parent_type` - Type of container for object defining the flow
- `obj_parent` - Name of container for flow object
- `module` - Module name where the flow is defined
- `import_path` - Python import path to the source file

#### If You Use Prefect Implementation

If you're using the default `PrefectFlowFinder`, **no changes are required** in your setup. The Prefect implementation automatically puts these attributes in `child_attributes` when discovering flows.

To access these attributes from discovered flows:
```python
from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder

finder = PrefectFlowFinder("path/to/flows")
flows = finder.find_flows()

for flow in flows:
    # Access implementation-specific attributes via child_attributes
    obj_type = flow.child_attributes.get("obj_type")  # "function" or "method"
    obj_name = flow.child_attributes.get("obj_name")  # function/method name
    module = flow.child_attributes.get("module")      # module name
    import_path = flow.child_attributes.get("import_path")  # import path
```

#### If You Create FlowDetails Manually

If you manually create `FlowDetails` objects, you need to update your code:

**Before (v0.x):**
```python
flow = FlowDetails(
    name="my_flow",
    original_name="my-flow", 
    description="Example flow",
    obj_type="function",
    obj_name="my_function",
    obj_parent_type="module",
    obj_parent="my_module",
    id="flow_123",
    module="my_module",
    source_path="/path/to/file.py",
    source_relative="file.py",
    import_path="my_module.file"
)
```

**After (v1.0+):**
```python
flow = FlowDetails(
    name="my_flow",
    original_name="my-flow",
    description="Example flow", 
    id="flow_123",
    source_path="/path/to/file.py",
    source_relative="file.py",
    child_attributes={
        "obj_type": "function",
        "obj_name": "my_function", 
        "obj_parent_type": "module",
        "obj_parent": "my_module",
        "module": "my_module",
        "import_path": "my_module.file"
    }
)
```

### Custom DeploymentFinder Implementation

Create a custom `DeploymentFinder` subclass to discover deployments in your environment:

```python
# .acme-portal-sdk/deployment_finder.py
from typing import List
from acme_portal_sdk.deployment_finder import DeploymentFinder, DeploymentDetails

class CustomDeploymentFinder(DeploymentFinder):
    """Custom deployment finder that discovers deployments with resource and region metadata."""
    
    def get_deployments(self, project_name: str, branch_name: str, env: str) -> List[DeploymentDetails]:
        # Sample implementation that returns deployments with custom metadata
        deployments = []
        
        # Example: production deployment with high resources
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
                # Custom metadata for your specific needs
                "region": "us-west-2",  # Custom region
                "cpu_limit": "4000m",   # High CPU limit for production
                "memory_limit": "8Gi",
                "health_check_enabled": True,
            }
        ))
        
        # Example: development deployment with standard resources
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
                    # Custom metadata for your specific needs
                    "region": "us-east-1",  # Standard region for dev
                    "cpu_limit": "1000m",   # Lower CPU limit for dev
                    "memory_limit": "2Gi",
                    "health_check_enabled": False,
                }
            ))
        
        return deployments

# Create the instance
deployment_finder = CustomDeploymentFinder()
```

### Custom DeployWorkflow Implementation

Both [`DeployWorkflow`](../developer/api-reference.md#acme_portal_sdk.flow_deploy.DeployWorkflow) and [`PromoteWorkflow`](../developer/api-reference.md#acme_portal_sdk.deployment_promote.PromoteWorkflow) use flexible signatures (`*args, **kwargs`) allowing custom implementations to accept additional parameters beyond the standard ones.

```python
# .acme-portal-sdk/flow_deploy.py
from typing import Optional, Dict, Any, List
from acme_portal_sdk.flow_deploy import DeployWorkflow

class CustomDeployWorkflow(DeployWorkflow):
    """Custom deployment workflow with environment-specific configuration and notifications."""
    
    def __init__(self, notification_webhook: Optional[str] = None):
        self.notification_webhook = notification_webhook
    
    def run(self, *args, **kwargs) -> Optional[str]:
        # Extract standard parameters with flexible argument handling
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        ref = kwargs.get('ref', args[1] if len(args) > 1 else 'main')
        
        # Accept custom parameters
        environment = kwargs.get('environment', 'dev')
        config = kwargs.get('deployment_config', {})
        dry_run = kwargs.get('dry_run', False)
        notification_channels = kwargs.get('notification_channels', [])
        
        # Sample deployment logic with custom functionality
        deployment_id = f"deploy_{hash(f'{flows}_{ref}_{environment}')}"
        
        print(f"Starting deployment {deployment_id}")
        print(f"  Flows: {flows}")
        print(f"  Reference: {ref}")
        print(f"  Environment: {environment}")
        print(f"  Configuration: {config}")
        
        if dry_run:
            print("  DRY RUN - No actual deployment performed")
            return f"dry_run_{deployment_id}"
        
        # Simulate environment-specific deployment steps
        if environment == "prod":
            print("  Performing production deployment with safety checks...")
            # Add production-specific logic like approval workflows
            self._validate_production_deployment(flows, config)
        else:
            print(f"  Performing {environment} deployment...")
        
        # Send notifications if configured
        if notification_channels:
            self._send_notifications(notification_channels, deployment_id, flows, environment)
        
        print(f"  Deployment {deployment_id} completed successfully")
        return deployment_id
    
    def _validate_production_deployment(self, flows: List[str], config: Dict[str, Any]):
        """Additional validation for production deployments."""
        required_config = ["resource_limits", "health_checks", "rollback_strategy"]
        missing = [key for key in required_config if key not in config]
        if missing:
            raise ValueError(f"Production deployment requires: {missing}")
    
    def _send_notifications(self, channels: List[str], deployment_id: str, flows: List[str], environment: str):
        """Send deployment notifications to specified channels."""
        message = f"Deployment {deployment_id} completed for flows {flows} in {environment}"
        for channel in channels:
            print(f"  Notification sent to {channel}: {message}")

# Create the instance
deploy = CustomDeployWorkflow(notification_webhook="https://hooks.slack.com/...")
```

### Custom PromoteWorkflow Implementation

```python
# .acme-portal-sdk/deployment_promote.py
from typing import Optional, List, Dict, Any
from acme_portal_sdk.deployment_promote import PromoteWorkflow

class CustomPromoteWorkflow(PromoteWorkflow):
    """Custom promotion workflow with approval gates and validation."""
    
    def __init__(self, require_approval: bool = True):
        self.require_approval = require_approval
    
    def run(self, *args, **kwargs) -> Optional[str]:
        # Extract standard parameters with flexible argument handling
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        source_env = kwargs.get('source_env', args[1] if len(args) > 1 else 'dev')
        target_env = kwargs.get('target_env', args[2] if len(args) > 2 else 'prod')
        ref = kwargs.get('ref', args[3] if len(args) > 3 else 'main')
        
        # Accept custom parameters
        project_name = kwargs.get('project_name', 'default-project')
        branch_name = kwargs.get('branch_name', 'main')
        auto_approve = kwargs.get('auto_approve', False)
        validation_rules = kwargs.get('validation_rules', [])
        
        # Sample promotion logic with custom functionality
        promotion_id = f"promote_{hash(f'{flows}_{source_env}_{target_env}_{ref}')}"
        
        print(f"Starting promotion {promotion_id}")
        print(f"  Flows: {flows}")
        print(f"  Source Environment: {source_env}")
        print(f"  Target Environment: {target_env}")
        print(f"  Reference: {ref}")
        print(f"  Project: {project_name}")
        
        # Run custom validation rules
        if validation_rules:
            print("  Running validation rules...")
            for rule in validation_rules:
                self._run_validation_rule(rule, flows, source_env, target_env)
        
        # Handle approval requirements
        if self.require_approval and not auto_approve:
            approval_status = self._request_approval(promotion_id, flows, source_env, target_env)
            if not approval_status:
                print(f"  Promotion {promotion_id} rejected or timed out")
                return None
        
        # Simulate promotion steps
        print("  Extracting source deployment configuration...")
        source_config = self._get_source_deployment_config(flows, source_env)
        
        print("  Applying target environment settings...")
        target_config = self._apply_target_environment_settings(source_config, target_env)
        
        print("  Creating target deployments...")
        # Simulate deployment creation
        for flow in flows:
            print(f"    Creating deployment for {flow} in {target_env}")
        
        print(f"  Promotion {promotion_id} completed successfully")
        return promotion_id
    
    def _run_validation_rule(self, rule: str, flows: List[str], source_env: str, target_env: str):
        """Run a custom validation rule."""
        print(f"    Validating rule: {rule}")
        # Example validation logic
        if rule == "security_scan" and target_env == "prod":
            print("      Security scan passed")
        elif rule == "performance_test":
            print("      Performance test passed")
    
    def _request_approval(self, promotion_id: str, flows: List[str], source_env: str, target_env: str) -> bool:
        """Request approval for the promotion (simulated)."""
        print(f"    Approval requested for promotion from {source_env} to {target_env}")
        print(f"    Flows requiring approval: {flows}")
        # Simulate approval (in real implementation, this would integrate with approval systems)
        return True
    
    def _get_source_deployment_config(self, flows: List[str], source_env: str) -> Dict[str, Any]:
        """Extract configuration from source deployments."""
        return {
            "version": "1.2.3",
            "commit_hash": "abc123def456",
            "resource_limits": {"cpu": "1000m", "memory": "2Gi"},
            "environment_vars": {"ENV": source_env}
        }
    
    def _apply_target_environment_settings(self, source_config: Dict[str, Any], target_env: str) -> Dict[str, Any]:
        """Apply target environment specific settings."""
        config = source_config.copy()
        config["environment_vars"]["ENV"] = target_env
        
        # Apply environment-specific resource scaling
        if target_env == "prod":
            config["resource_limits"]["cpu"] = "4000m"
            config["resource_limits"]["memory"] = "8Gi"
        
        return config

# Create the instance
promote = CustomPromoteWorkflow(require_approval=True)
```

### Usage Examples

#### Basic Usage
```python
# Standard calls work with any implementation
deploy_workflow.run(["flow1", "flow2"], "main")
promote_workflow.run(["flow1"], "dev", "prod", "main")
```

#### Extended Usage with Custom Parameters
```python
# Use additional parameters as needed
deploy_workflow.run(
    flows_to_deploy=["data_ingestion", "data_transformation"],
    ref="main",
    environment="staging",
    deployment_config={
        "resource_limits": {"cpu": "2000m", "memory": "4Gi"},
        "health_checks": {"enabled": True, "timeout": 30},
        "rollback_strategy": "automatic"
    },
    dry_run=False,
    notification_channels=["slack", "email"]
)

promote_workflow.run(
    flows_to_deploy=["data_ingestion"],
    source_env="staging",
    target_env="prod",
    ref="v1.2.3",
    project_name="analytics-platform",
    branch_name="main",
    auto_approve=False,
    validation_rules=["security_scan", "performance_test"]
)
```

## Using GitHub Workflows for Deployment and Promotion

For detailed instructions on using GitHub Actions as a provider for `DeployWorkflow` and `PromoteWorkflow`, refer to the [GitHub Workflows Guide](github-workflows.md).