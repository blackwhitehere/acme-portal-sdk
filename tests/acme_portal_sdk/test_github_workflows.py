"""Tests for GitHub Actions workflow implementations."""

import pytest
from unittest.mock import Mock, patch

from acme_portal_sdk.github.github_workflow import (
    GithubActionsDeployWorkflow,
    GithubActionsPromoteWorkflow
)


class TestGithubActionsWorkflows:
    """Test GitHub Actions workflow implementations."""
    
    def test_deploy_workflow_backward_compatibility(self):
        """Test that the GitHub Actions deploy workflow maintains backward compatibility."""
        with patch('acme_portal_sdk.github.github_workflow.CommandExecutor') as mock_executor_class:
            # Mock the command executor
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor
            mock_executor.execute.return_value = ("gh version", "")
            
            # Create workflow instance
            workflow = GithubActionsDeployWorkflow()
            
            # Mock the workflow service trigger method
            with patch.object(workflow.workflow_service, 'trigger_workflow') as mock_trigger:
                mock_trigger.return_value = "https://github.com/repo/actions/runs/123"
                
                # Test old-style call (positional args)
                result = workflow.run(["flow1", "flow2"], "main")
                
                assert result == "https://github.com/repo/actions/runs/123"
                mock_trigger.assert_called_once_with(
                    "deploy.yml",
                    {"flows-to-deploy": "flow1,flow2"},
                    "main"
                )
    
    def test_deploy_workflow_with_keyword_args(self):
        """Test GitHub Actions deploy workflow with keyword arguments."""
        with patch('acme_portal_sdk.github.github_workflow.CommandExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor
            mock_executor.execute.return_value = ("gh version", "")
            
            workflow = GithubActionsDeployWorkflow()
            
            with patch.object(workflow.workflow_service, 'trigger_workflow') as mock_trigger:
                mock_trigger.return_value = "https://github.com/repo/actions/runs/456"
                
                # Test new-style call (keyword args)
                result = workflow.run(
                    flows_to_deploy=["flow1"], 
                    ref="develop"
                )
                
                assert result == "https://github.com/repo/actions/runs/456"
                mock_trigger.assert_called_once_with(
                    "deploy.yml",
                    {"flows-to-deploy": "flow1"},
                    "develop"
                )
    
    def test_deploy_workflow_default_ref(self):
        """Test GitHub Actions deploy workflow uses default ref when none provided."""
        with patch('acme_portal_sdk.github.github_workflow.CommandExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor
            mock_executor.execute.return_value = ("gh version", "")
            
            workflow = GithubActionsDeployWorkflow(default_ref="staging")
            
            with patch.object(workflow.workflow_service, 'trigger_workflow') as mock_trigger:
                mock_trigger.return_value = "https://github.com/repo/actions/runs/789"
                
                # Test with flows only, should use default ref
                result = workflow.run(flows_to_deploy=["flow1"])
                
                assert result == "https://github.com/repo/actions/runs/789"
                mock_trigger.assert_called_once_with(
                    "deploy.yml",
                    {"flows-to-deploy": "flow1"},
                    "staging"
                )
    
    def test_promote_workflow_backward_compatibility(self):
        """Test that the GitHub Actions promote workflow maintains backward compatibility."""
        with patch('acme_portal_sdk.github.github_workflow.CommandExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor
            mock_executor.execute.return_value = ("gh version", "")
            
            workflow = GithubActionsPromoteWorkflow()
            
            with patch.object(workflow.workflow_service, 'trigger_workflow') as mock_trigger:
                mock_trigger.return_value = "https://github.com/repo/actions/runs/321"
                
                # Test old-style call (positional args)
                result = workflow.run(["flow1"], "dev", "prod", "main")
                
                assert result == "https://github.com/repo/actions/runs/321"
                mock_trigger.assert_called_once_with(
                    "promote.yml",
                    {
                        "flows-to-deploy": "flow1",
                        "source-env": "dev",
                        "target-env": "prod"
                    },
                    "main"
                )
    
    def test_promote_workflow_with_keyword_args(self):
        """Test GitHub Actions promote workflow with keyword arguments."""
        with patch('acme_portal_sdk.github.github_workflow.CommandExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor
            mock_executor.execute.return_value = ("gh version", "")
            
            workflow = GithubActionsPromoteWorkflow()
            
            with patch.object(workflow.workflow_service, 'trigger_workflow') as mock_trigger:
                mock_trigger.return_value = "https://github.com/repo/actions/runs/654"
                
                # Test new-style call (keyword args)
                result = workflow.run(
                    flows_to_deploy=["flow1", "flow2"],
                    source_env="staging",
                    target_env="production",
                    ref="release/v1.0"
                )
                
                assert result == "https://github.com/repo/actions/runs/654"
                mock_trigger.assert_called_once_with(
                    "promote.yml",
                    {
                        "flows-to-deploy": "flow1,flow2",
                        "source-env": "staging",
                        "target-env": "production"
                    },
                    "release/v1.0"
                )
    
    def test_promote_workflow_missing_required_params(self):
        """Test that promote workflow raises error when required params are missing."""
        with patch('acme_portal_sdk.github.github_workflow.CommandExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor
            mock_executor.execute.return_value = ("gh version", "")
            
            workflow = GithubActionsPromoteWorkflow()
            
            # Test missing required parameters
            with pytest.raises(ValueError, match="source_env, target_env, and ref are required"):
                workflow.run(flows_to_deploy=["flow1"])