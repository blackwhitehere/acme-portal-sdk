"""Integration test showing the practical benefits of flexible signatures."""

from typing import Any, Optional, List

from acme_portal_sdk.flow_deploy import DeployWorkflow
from acme_portal_sdk.deployment_promote import PromoteWorkflow


class CustomDeployWorkflow(DeployWorkflow):
    """Example of a custom implementation that needs additional parameters."""
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Custom deploy implementation requiring extra parameters."""
        # Extract parameters flexibly
        flows_to_deploy = kwargs.get('flows_to_deploy', args[0] if args else [])
        ref = kwargs.get('ref', args[1] if len(args) > 1 else 'main')
        
        # Custom parameters that the rigid signature wouldn't allow
        environment = kwargs.get('environment', 'dev')
        notification_webhook = kwargs.get('notification_webhook')
        deployment_config = kwargs.get('deployment_config', {})
        retry_count = kwargs.get('retry_count', 3)
        
        # Simulate deployment logic
        print(f"Deploying flows {flows_to_deploy} to {environment} from {ref}")
        if notification_webhook:
            print(f"Will notify via webhook: {notification_webhook}")
        print(f"Using config: {deployment_config}, retry count: {retry_count}")
        
        return f"deployed-{'-'.join(flows_to_deploy)}-{environment}"


class CustomPromoteWorkflow(PromoteWorkflow):
    """Example of a custom implementation that needs additional parameters."""
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Custom promote implementation requiring extra parameters."""
        # Extract standard parameters
        flows_to_deploy = kwargs.get('flows_to_deploy', args[0] if args else [])
        source_env = kwargs.get('source_env', args[1] if len(args) > 1 else None)
        target_env = kwargs.get('target_env', args[2] if len(args) > 2 else None)
        ref = kwargs.get('ref', args[3] if len(args) > 3 else 'main')
        
        # Custom parameters for advanced promotion workflows
        approval_required = kwargs.get('approval_required', True)
        rollback_plan = kwargs.get('rollback_plan')
        health_checks = kwargs.get('health_checks', [])
        promotion_window = kwargs.get('promotion_window')
        
        # Simulate promotion logic
        print(f"Promoting {flows_to_deploy} from {source_env} to {target_env} (ref: {ref})")
        if approval_required:
            print("Waiting for approval...")
        if rollback_plan:
            print(f"Rollback plan: {rollback_plan}")
        if health_checks:
            print(f"Will run health checks: {health_checks}")
        if promotion_window:
            print(f"Promotion window: {promotion_window}")
        
        return f"promoted-{'-'.join(flows_to_deploy)}-{source_env}-to-{target_env}"


def test_real_world_usage_scenarios():
    """Test scenarios that show the practical benefits of flexible signatures."""
    print("=== Testing Flexible Workflow Signatures ===\n")
    
    # Scenario 1: Custom deploy workflow with additional configuration
    print("Scenario 1: Custom deployment with extra parameters")
    deploy_workflow = CustomDeployWorkflow()
    
    result = deploy_workflow.run(
        flows_to_deploy=['user-service', 'auth-service'],
        ref='feature/new-auth',
        environment='staging', 
        notification_webhook='https://hooks.slack.com/webhooks/...',
        deployment_config={
            'replicas': 3,
            'memory_limit': '512Mi',
            'cpu_limit': '500m'
        },
        retry_count=5
    )
    print(f"Result: {result}\n")
    
    # Scenario 2: Backward compatibility still works
    print("Scenario 2: Backward compatibility with old signature")
    result = deploy_workflow.run(['legacy-flow'], 'main')
    print(f"Result: {result}\n")
    
    # Scenario 3: Complex promotion workflow
    print("Scenario 3: Advanced promotion with custom parameters")
    promote_workflow = CustomPromoteWorkflow()
    
    result = promote_workflow.run(
        flows_to_deploy=['payment-processor', 'order-service'],
        source_env='staging',
        target_env='production',
        ref='release/v2.1.0',
        approval_required=True,
        rollback_plan='auto-rollback-on-failure',
        health_checks=['api-health', 'database-connectivity', 'external-service-check'],
        promotion_window='2024-01-15T02:00:00Z to 2024-01-15T04:00:00Z'
    )
    print(f"Result: {result}\n")
    
    # Scenario 4: Using call method with mixed args
    print("Scenario 4: Using __call__ method with mixed arguments")
    result = promote_workflow(
        ['data-pipeline'], 
        'dev',
        target_env='test',
        ref='main',
        approval_required=False,
        health_checks=['data-quality-check']
    )
    print(f"Result: {result}\n")
    
    print("=== All scenarios completed successfully! ===")


if __name__ == "__main__":
    test_real_world_usage_scenarios()