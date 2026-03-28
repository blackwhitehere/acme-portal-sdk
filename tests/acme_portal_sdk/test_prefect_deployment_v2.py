"""Tests for the v2 Prefect deployment paradigm."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from acme_portal_sdk.prefect.deployment_script_generator import DeploymentScriptGenerator
from acme_portal_sdk.prefect.deployment_script_executor import DeploymentScriptExecutor


class TestDeploymentScriptGenerator:
    """Test deployment script generation."""
    
    def test_script_path_generation(self):
        """Test that script paths are generated correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = DeploymentScriptGenerator(Path(temp_dir))
            
            # Mock deployment info
            deploy_info = Mock()
            deploy_info.name = "myproject--main--my-flow--prod"
            deploy_info.flow_name = "my_flow"
            
            expected_path = Path(temp_dir) / "myproject" / "prod" / "my_flow_deploy.py"
            actual_path = generator._get_script_path(deploy_info)
            
            assert actual_path == expected_path
    
    def test_script_path_fallback(self):
        """Test script path generation with non-standard naming."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = DeploymentScriptGenerator(Path(temp_dir))
            
            # Mock deployment info with non-standard name
            deploy_info = Mock()
            deploy_info.name = "simple-name"
            deploy_info.flow_name = "my_flow"
            
            expected_path = Path(temp_dir) / "default" / "default" / "my_flow_deploy.py"
            actual_path = generator._get_script_path(deploy_info)
            
            assert actual_path == expected_path
    
    def test_generate_script_content(self):
        """Test that script content is generated correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = DeploymentScriptGenerator(Path(temp_dir))
            
            # Mock flow function
            mock_flow = Mock()
            mock_flow.__module__ = "my_module"
            mock_flow.__name__ = "my_flow"
            
            # Mock deployment info
            deploy_info = Mock()
            deploy_info.name = "myproject--main--my-flow--prod"
            deploy_info.flow_name = "my_flow"
            deploy_info.description = "Test flow"
            deploy_info.work_pool_name = "test-pool"
            deploy_info.work_queue_name = "test-queue"
            deploy_info.cron = None
            deploy_info.parameters = {"param1": "value1"}
            deploy_info.job_variables = {"var1": "value1"}
            deploy_info.image_uri = "test:latest"
            deploy_info.tags = ["test"]
            deploy_info.version = "1.0.0"
            deploy_info.paused = False
            deploy_info.concurrency_limit = 1
            deploy_info.flow_function = mock_flow
            
            script_content = generator._generate_script_content(deploy_info, {})
            
            # Check that key elements are in the script
            assert "from my_module import my_flow as flow_function" in script_content
            assert 'DEPLOYMENT_NAME = "myproject--main--my-flow--prod"' in script_content
            assert "DESCRIPTION = 'Test flow'" in script_content
            assert "WORK_POOL_NAME = 'test-pool'" in script_content
            assert "def deploy():" in script_content
            assert "flow_function.deploy(" in script_content
    
    def test_custom_section_preservation(self):
        """Test that custom sections are preserved when regenerating scripts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = DeploymentScriptGenerator(Path(temp_dir))
            
            # Create a test script with custom content
            test_script = Path(temp_dir) / "test_deploy.py"
            test_content = '''
# CUSTOM_DEPLOYMENT_CONFIG - Add your custom deployment logic here

def custom_pre_deploy_hook():
    """Custom logic."""
    print("Custom pre-deploy logic")

def get_custom_deploy_args():
    """Custom args."""
    return {"custom_arg": "custom_value"}

# END CUSTOM_DEPLOYMENT_CONFIG
'''
            test_script.write_text(test_content)
            
            custom_sections = generator._extract_custom_sections(test_script)
            
            assert "custom_deployment_config" in custom_sections
            assert "Custom pre-deploy logic" in custom_sections["custom_deployment_config"]
            assert "custom_value" in custom_sections["custom_deployment_config"]


class TestDeploymentScriptExecutor:
    """Test deployment script execution and scanning."""
    
    def test_find_deployment_scripts(self):
        """Test finding deployment scripts in directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            executor = DeploymentScriptExecutor(temp_path)
            
            # Create test directory structure
            project_dir = temp_path / "myproject"
            env_dir = project_dir / "prod"
            env_dir.mkdir(parents=True)
            
            # Create test scripts
            script1 = env_dir / "flow1_deploy.py"
            script2 = env_dir / "flow2_deploy.py"
            script1.write_text("# Test script 1")
            script2.write_text("# Test script 2")
            
            # Find all scripts
            scripts = executor.find_deployment_scripts()
            assert len(scripts) == 2
            assert script1 in scripts
            assert script2 in scripts
            
            # Filter by project
            scripts = executor.find_deployment_scripts(project_name="myproject")
            assert len(scripts) == 2
            
            # Filter by environment
            scripts = executor.find_deployment_scripts(env="prod")
            assert len(scripts) == 2
            
            # Filter by flow names
            scripts = executor.find_deployment_scripts(flow_names=["flow1"])
            assert len(scripts) == 1
            assert script1 in scripts
    
    def test_find_scripts_no_directory(self):
        """Test finding scripts when directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "nonexistent"
            executor = DeploymentScriptExecutor(temp_path)
            
            scripts = executor.find_deployment_scripts()
            assert scripts == []
    
    @patch('subprocess.run')
    def test_execute_script_success(self, mock_run):
        """Test successful script execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            executor = DeploymentScriptExecutor(temp_path)
            
            # Mock successful subprocess run
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Deployment successful"
            mock_run.return_value.stderr = ""
            
            script_path = temp_path / "test_deploy.py"
            script_path.write_text("print('test')")
            
            result = executor.execute_script(script_path)
            assert result is True
            mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_execute_script_failure(self, mock_run):
        """Test failed script execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            executor = DeploymentScriptExecutor(temp_path)
            
            # Mock failed subprocess run
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Error occurred"
            
            script_path = temp_path / "test_deploy.py"
            script_path.write_text("print('test')")
            
            result = executor.execute_script(script_path)
            assert result is False
            mock_run.assert_called_once()
    
    def test_validate_script_valid(self):
        """Test validation of a valid deployment script."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            executor = DeploymentScriptExecutor(temp_path)
            
            # Create a valid script with deploy function
            script_path = temp_path / "valid_deploy.py"
            script_content = '''
def deploy():
    """Deploy function."""
    return "deployed"
'''
            script_path.write_text(script_content)
            
            result = executor.validate_script(script_path)
            assert result is True
    
    def test_validate_script_invalid(self):
        """Test validation of invalid deployment script."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            executor = DeploymentScriptExecutor(temp_path)
            
            # Create an invalid script without deploy function
            script_path = temp_path / "invalid_deploy.py"
            script_content = '''
def some_other_function():
    """Not a deploy function."""
    pass
'''
            script_path.write_text(script_content)
            
            result = executor.validate_script(script_path)
            assert result is False


# Integration test without Prefect dependencies
class TestV2Integration:
    """Test integration of v2 components without Prefect dependencies."""
    
    def test_template_import(self):
        """Test that the deployment template can be imported."""
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        assert DEPLOYMENT_SCRIPT_TEMPLATE is not None
        assert "def deploy():" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "flow_function.deploy(" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "CUSTOM_DEPLOYMENT_CONFIG" in DEPLOYMENT_SCRIPT_TEMPLATE
    
    def test_script_directory_creation(self):
        """Test that script directories are created properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test generator creates directories
            generator = DeploymentScriptGenerator(temp_path / "scripts")
            assert (temp_path / "scripts").exists()
            
            # Test executor works with existing directories
            executor = DeploymentScriptExecutor(temp_path / "scripts")
            scripts = executor.find_deployment_scripts()
            assert isinstance(scripts, list)