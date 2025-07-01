# Workflow Signature Flexibility Examples

This document demonstrates how the flexible `*args, **kwargs` signatures in `DeployWorkflow` and `PromoteWorkflow` allow for more extensible implementations.

## Before (Rigid Signature)

```python
# Old rigid signatures were restrictive
class DeployWorkflow(ABC):
    @abstractmethod
    def run(self, flows_to_deploy: List[str], ref: str) -> Optional[str]:
        pass

class PromoteWorkflow(ABC):
    @abstractmethod  
    def run(self, flows_to_deploy: List[str], source_env: str, target_env: str, ref: str) -> Optional[str]:
        pass
```

**Problems:**
- User pipelines couldn't pass additional required attributes
- Implementations couldn't extend functionality without breaking the interface
- Hard to support different deployment patterns

## After (Flexible Signature)

```python
# New flexible signatures allow for extension
class DeployWorkflow(ABC):
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        pass

class PromoteWorkflow(ABC):
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        pass
```

## Usage Examples

### 1. Backward Compatibility

```python
# Old usage still works
deploy_workflow.run(["flow1", "flow2"], "main")
promote_workflow.run(["flow1"], "dev", "prod", "main")
```

### 2. Extended Functionality

```python
# Now possible: Custom deployment with additional configuration
deploy_workflow.run(
    flows_to_deploy=["user-service", "auth-service"],
    ref="feature/new-auth",
    environment="staging",
    notification_webhook="https://hooks.slack.com/webhooks/...",
    deployment_config={
        "replicas": 3,
        "memory_limit": "512Mi",
        "cpu_limit": "500m"
    },
    retry_count=5
)

# Advanced promotion with custom parameters
promote_workflow.run(
    flows_to_deploy=["payment-processor"],
    source_env="staging",
    target_env="production", 
    ref="release/v2.1.0",
    approval_required=True,
    rollback_plan="auto-rollback-on-failure",
    health_checks=["api-health", "database-connectivity"],
    promotion_window="2024-01-15T02:00:00Z to 2024-01-15T04:00:00Z"
)
```

### 3. Custom Implementation Example

```python
class AdvancedDeployWorkflow(DeployWorkflow):
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        # Extract standard parameters
        flows = kwargs.get('flows_to_deploy', args[0] if args else [])
        ref = kwargs.get('ref', args[1] if len(args) > 1 else 'main')
        
        # Handle custom parameters that rigid signature couldn't support
        environment = kwargs.get('environment', 'dev')
        config = kwargs.get('deployment_config', {})
        notifications = kwargs.get('notification_webhook')
        
        # Your custom deployment logic here
        return self.deploy_with_advanced_features(flows, ref, environment, config, notifications)
```

## Benefits

1. **Extensibility**: Implementations can support additional parameters without changing the abstract interface
2. **Backward Compatibility**: Existing code continues to work unchanged
3. **Flexibility**: Different deployment strategies can use different parameter sets
4. **Future-Proofing**: New requirements can be accommodated without breaking changes

This change addresses the core issue that "the interface is too rigid in case user pipelines require different attributes."