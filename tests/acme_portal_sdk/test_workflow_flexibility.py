"""Tests for flexible workflow method signatures."""

import pytest
from typing import Any, Optional

from acme_portal_sdk.flow_deploy import DeployWorkflow
from acme_portal_sdk.deployment_promote import PromoteWorkflow


class MockDeployWorkflow(DeployWorkflow):
    """Mock implementation of DeployWorkflow for testing."""
    
    def __init__(self):
        self.last_args = None
        self.last_kwargs = None
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Store the arguments for verification."""
        self.last_args = args
        self.last_kwargs = kwargs
        return "mock-deploy-url"


class MockPromoteWorkflow(PromoteWorkflow):
    """Mock implementation of PromoteWorkflow for testing."""
    
    def __init__(self):
        self.last_args = None
        self.last_kwargs = None
    
    def run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        """Store the arguments for verification."""
        self.last_args = args
        self.last_kwargs = kwargs
        return "mock-promote-url"


class TestDeployWorkflowFlexibility:
    """Test the flexibility of DeployWorkflow signatures."""
    
    def test_deploy_with_minimal_args(self):
        """Test DeployWorkflow with minimal positional arguments."""
        workflow = MockDeployWorkflow()
        result = workflow.run(["flow1", "flow2"], "main")
        
        assert result == "mock-deploy-url"
        assert workflow.last_args == (["flow1", "flow2"], "main")
        assert workflow.last_kwargs == {}
    
    def test_deploy_with_keyword_args(self):
        """Test DeployWorkflow with keyword arguments."""
        workflow = MockDeployWorkflow()
        result = workflow.run(
            flows_to_deploy=["flow1"], 
            ref="develop", 
            project_name="test-project"
        )
        
        assert result == "mock-deploy-url"
        assert workflow.last_args == ()
        assert workflow.last_kwargs == {
            "flows_to_deploy": ["flow1"],
            "ref": "develop",
            "project_name": "test-project"
        }
    
    def test_deploy_with_mixed_args(self):
        """Test DeployWorkflow with mixed positional and keyword arguments."""
        workflow = MockDeployWorkflow()
        result = workflow.run(
            ["flow1"],
            ref="main", 
            environment="prod",
            extra_param="value"
        )
        
        assert result == "mock-deploy-url"
        assert workflow.last_args == (["flow1"],)
        assert workflow.last_kwargs == {
            "ref": "main",
            "environment": "prod", 
            "extra_param": "value"
        }
    
    def test_deploy_via_call_method(self):
        """Test DeployWorkflow called via __call__ method."""
        workflow = MockDeployWorkflow()
        result = workflow(["flow1"], ref="main", custom_attr="test")
        
        assert result == "mock-deploy-url"
        assert workflow.last_args == (["flow1"],)
        assert workflow.last_kwargs == {"ref": "main", "custom_attr": "test"}


class TestPromoteWorkflowFlexibility:
    """Test the flexibility of PromoteWorkflow signatures."""
    
    def test_promote_with_minimal_args(self):
        """Test PromoteWorkflow with minimal positional arguments."""
        workflow = MockPromoteWorkflow()
        result = workflow.run(["flow1"], "dev", "prod", "main")
        
        assert result == "mock-promote-url"
        assert workflow.last_args == (["flow1"], "dev", "prod", "main")
        assert workflow.last_kwargs == {}
    
    def test_promote_with_keyword_args(self):
        """Test PromoteWorkflow with keyword arguments."""
        workflow = MockPromoteWorkflow()
        result = workflow.run(
            flows_to_deploy=["flow1"],
            source_env="dev",
            target_env="prod", 
            ref="main",
            project_name="test-project"
        )
        
        assert result == "mock-promote-url"
        assert workflow.last_args == ()
        assert workflow.last_kwargs == {
            "flows_to_deploy": ["flow1"],
            "source_env": "dev",
            "target_env": "prod",
            "ref": "main",
            "project_name": "test-project"
        }
    
    def test_promote_with_extra_params(self):
        """Test PromoteWorkflow with additional custom parameters."""
        workflow = MockPromoteWorkflow()
        result = workflow.run(
            flows_to_deploy=["flow1", "flow2"],
            source_env="staging",
            target_env="production",
            ref="release/v1.0",
            branch_name="release",
            commit_hash="abc123",
            notification_channel="slack"
        )
        
        assert result == "mock-promote-url"
        assert workflow.last_args == ()
        assert workflow.last_kwargs == {
            "flows_to_deploy": ["flow1", "flow2"],
            "source_env": "staging",
            "target_env": "production",
            "ref": "release/v1.0",
            "branch_name": "release",
            "commit_hash": "abc123",
            "notification_channel": "slack"
        }
    
    def test_promote_via_call_method(self):
        """Test PromoteWorkflow called via __call__ method."""
        workflow = MockPromoteWorkflow()
        result = workflow(
            ["flow1"], 
            "dev", 
            "prod", 
            ref="main",
            extra_data={"key": "value"}
        )
        
        assert result == "mock-promote-url"
        assert workflow.last_args == (["flow1"], "dev", "prod")
        assert workflow.last_kwargs == {
            "ref": "main",
            "extra_data": {"key": "value"}
        }


class TestBackwardCompatibility:
    """Test that existing usage patterns still work."""
    
    def test_deploy_old_style_positional(self):
        """Test that old-style positional arguments still work for deploy."""
        workflow = MockDeployWorkflow()
        # Simulate old usage: deploy.run(flows_list, ref)
        result = workflow.run(["flow1", "flow2"], "main")
        
        assert result == "mock-deploy-url"
        assert workflow.last_args == (["flow1", "flow2"], "main")
    
    def test_promote_old_style_positional(self):
        """Test that old-style positional arguments still work for promote."""
        workflow = MockPromoteWorkflow()
        # Simulate old usage: promote.run(flows_list, source_env, target_env, ref)
        result = workflow.run(["flow1"], "dev", "prod", "main")
        
        assert result == "mock-promote-url"
        assert workflow.last_args == (["flow1"], "dev", "prod", "main")