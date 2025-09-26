"""Tests for the v2 Prefect deployment template (no Prefect dependencies)."""

import tempfile
from pathlib import Path


class TestDeploymentTemplate:
    """Test deployment script template."""
    
    def test_template_import(self):
        """Test that the deployment template can be imported."""
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        assert DEPLOYMENT_SCRIPT_TEMPLATE is not None
        assert isinstance(DEPLOYMENT_SCRIPT_TEMPLATE, str)
        
        # Check key template elements
        assert "def deploy():" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "flow_function.deploy(" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "CUSTOM_DEPLOYMENT_CONFIG" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "def custom_pre_deploy_hook():" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "def custom_post_deploy_hook():" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "get_custom_deploy_args" in DEPLOYMENT_SCRIPT_TEMPLATE
    
    def test_template_formatting(self):
        """Test that template can be formatted with parameters."""
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        # Test parameters
        params = {
            'flow_name': 'test_flow',
            'generation_timestamp': '2024-01-01T00:00:00',
            'project_name': 'test_project',
            'env': 'test_env',
            'module_path': 'test.module',
            'function_name': 'test_function',
            'deployment_name': 'test-deployment',
            'description': 'Test deployment',
            'work_pool_name': 'test-pool',
            'work_queue_name': 'test-queue',
            'cron': None,
            'parameters': {'param1': 'value1'},
            'job_variables': {'var1': 'value1'},
            'image_uri': 'test:latest',
            'tags': ['test'],
            'version': '1.0.0',
            'paused': False,
            'concurrency_limit': 1,
        }
        
        # Format template
        formatted_script = DEPLOYMENT_SCRIPT_TEMPLATE.format(**params)
        
        # Check that formatting worked
        assert 'test_flow' in formatted_script
        assert 'test_project' in formatted_script
        assert 'test.module' in formatted_script
        assert 'test_function' in formatted_script
        assert 'test-deployment' in formatted_script
        assert "PARAMETERS = {'param1': 'value1'}" in formatted_script
        assert "JOB_VARIABLES = {'var1': 'value1'}" in formatted_script
        assert "IMAGE_URI = 'test:latest'" in formatted_script
        assert "TAGS = ['test']" in formatted_script
        assert "VERSION = '1.0.0'" in formatted_script
        assert "PAUSED = False" in formatted_script
        assert "CONCURRENCY_LIMIT = 1" in formatted_script
    
    def test_template_executable_structure(self):
        """Test that generated script has executable structure."""
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        # Simple formatting to create a valid Python file
        params = {
            'flow_name': 'test_flow',
            'generation_timestamp': '2024-01-01T00:00:00',
            'project_name': 'test_project',
            'env': 'test_env',
            'module_path': 'test.module',
            'function_name': 'test_function',
            'deployment_name': 'test-deployment',
            'description': 'Test deployment',
            'work_pool_name': 'test-pool',
            'work_queue_name': 'test-queue',
            'cron': None,
            'parameters': {},
            'job_variables': {},
            'image_uri': 'test:latest',
            'tags': [],
            'version': '1.0.0',
            'paused': False,
            'concurrency_limit': 1,
        }
        
        formatted_script = DEPLOYMENT_SCRIPT_TEMPLATE.format(**params)
        
        # Test that it's valid Python syntax by compiling it
        try:
            compile(formatted_script, '<string>', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Generated script has invalid Python syntax: {e}")
        
        # Test that it has the expected functions
        assert "def custom_pre_deploy_hook():" in formatted_script
        assert "def custom_post_deploy_hook():" in formatted_script
        assert "get_custom_deploy_args" in formatted_script
        assert "def deploy():" in formatted_script
        assert 'if __name__ == "__main__":' in formatted_script
    
    def test_custom_sections_markers(self):
        """Test that custom section markers are present."""
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        # Check for custom section markers
        assert "# CUSTOM_DEPLOYMENT_CONFIG" in DEPLOYMENT_SCRIPT_TEMPLATE
        assert "# END CUSTOM_DEPLOYMENT_CONFIG" in DEPLOYMENT_SCRIPT_TEMPLATE
        
        # Check that there's content between the markers
        start_marker = "# CUSTOM_DEPLOYMENT_CONFIG"
        end_marker = "# END CUSTOM_DEPLOYMENT_CONFIG"
        
        start_idx = DEPLOYMENT_SCRIPT_TEMPLATE.find(start_marker)
        end_idx = DEPLOYMENT_SCRIPT_TEMPLATE.find(end_marker)
        
        assert start_idx != -1, "Start marker not found"
        assert end_idx != -1, "End marker not found"
        assert start_idx < end_idx, "Markers are in wrong order"
        
        # Content between markers should contain function definitions
        custom_section = DEPLOYMENT_SCRIPT_TEMPLATE[start_idx:end_idx]
        assert "def custom_pre_deploy_hook():" in custom_section
        assert "def custom_post_deploy_hook():" in custom_section
        assert "get_custom_deploy_args" in custom_section


class TestScriptDirectoryCreation:
    """Test script directory handling without Prefect dependencies."""
    
    def test_directory_creation(self):
        """Test that directories can be created for scripts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test directory structure creation
            scripts_root = temp_path / "deployment_scripts"
            project_dir = scripts_root / "myproject"
            env_dir = project_dir / "prod"
            
            # Create directory structure
            env_dir.mkdir(parents=True, exist_ok=True)
            
            assert scripts_root.exists()
            assert project_dir.exists() 
            assert env_dir.exists()
            
            # Test creating script files
            script_path = env_dir / "test_flow_deploy.py"
            script_path.write_text("# Test deployment script\n")
            
            assert script_path.exists()
            assert script_path.is_file()
            assert script_path.suffix == ".py"
    
    def test_script_discovery_pattern(self):
        """Test script discovery patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test directory structure with scripts
            scripts_root = temp_path / "deployment_scripts"
            project1_prod = scripts_root / "project1" / "prod"
            project1_dev = scripts_root / "project1" / "dev"
            project2_prod = scripts_root / "project2" / "prod"
            
            project1_prod.mkdir(parents=True, exist_ok=True)
            project1_dev.mkdir(parents=True, exist_ok=True)
            project2_prod.mkdir(parents=True, exist_ok=True)
            
            # Create deployment scripts
            scripts = [
                project1_prod / "flow1_deploy.py",
                project1_prod / "flow2_deploy.py", 
                project1_dev / "flow1_deploy.py",
                project2_prod / "flow3_deploy.py",
                project1_prod / "not_a_deployment.py",  # Should not match pattern
            ]
            
            for script in scripts:
                script.write_text("# Test script")
            
            # Test script discovery
            all_deploy_scripts = list(scripts_root.rglob("*_deploy.py"))
            assert len(all_deploy_scripts) == 4  # Excludes not_a_deployment.py
            
            # Test project filtering
            project1_scripts = list((scripts_root / "project1").rglob("*_deploy.py"))
            assert len(project1_scripts) == 3
            
            # Test environment filtering  
            prod_scripts = list(scripts_root.rglob("prod/*_deploy.py"))
            assert len(prod_scripts) == 3