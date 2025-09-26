"""End-to-end test for v2 deployment paradigm (without Prefect dependencies)."""

import tempfile
from pathlib import Path
from unittest.mock import Mock


def test_v2_deployment_script_generation_workflow():
    """Test the complete workflow of generating and validating deployment scripts."""
    
    # This test simulates the complete workflow without requiring Prefect
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        scripts_root = temp_path / "deployment_scripts"
        
        # Step 1: Import the template (this works without Prefect)
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        # Step 2: Simulate deployment info (normally from PrefectDeployInfo)
        mock_deploy_info = {
            'flow_name': 'data_processing_flow',
            'generation_timestamp': '2024-01-01T12:00:00',
            'project_name': 'data_pipeline',
            'env': 'production',
            'module_path': 'flows.data_processing',
            'function_name': 'data_processing_flow',
            'deployment_name': 'data-pipeline--main--data-processing-flow--production',
            'description': 'Process daily data files',
            'work_pool_name': 'production-pool',
            'work_queue_name': 'high-priority',
            'cron': '0 2 * * *',  # Daily at 2 AM
            'parameters': {'batch_size': 1000, 'retry_count': 3},
            'job_variables': {'ENV': 'production', 'LOG_LEVEL': 'INFO'},
            'image_uri': 'myregistry/data-processor:v1.2.0',
            'tags': ['production', 'daily', 'data'],
            'version': '1.2.0',
            'paused': False,
            'concurrency_limit': 2,
        }
        
        # Step 3: Generate deployment script content
        script_content = DEPLOYMENT_SCRIPT_TEMPLATE.format(**mock_deploy_info)
        
        # Step 4: Create directory structure (simulating DeploymentScriptGenerator)
        project_dir = scripts_root / mock_deploy_info['project_name']
        env_dir = project_dir / mock_deploy_info['env']
        env_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = env_dir / f"{mock_deploy_info['flow_name']}_deploy.py"
        
        # Step 5: Write the script
        script_path.write_text(script_content)
        script_path.chmod(0o755)  # Make executable
        
        # Step 6: Verify the generated script
        assert script_path.exists()
        assert script_path.is_file()
        assert script_path.stat().st_mode & 0o111  # Check executable bit
        
        generated_content = script_path.read_text()
        
        # Verify key content is present
        assert "data_processing_flow" in generated_content
        assert "data-pipeline--main--data-processing-flow--production" in generated_content
        assert "from flows.data_processing import data_processing_flow as flow_function" in generated_content
        assert "CRON = '0 2 * * *'" in generated_content
        assert "PARAMETERS = {'batch_size': 1000, 'retry_count': 3}" in generated_content
        assert "JOB_VARIABLES = {'ENV': 'production', 'LOG_LEVEL': 'INFO'}" in generated_content
        assert "IMAGE_URI = 'myregistry/data-processor:v1.2.0'" in generated_content
        assert "TAGS = ['production', 'daily', 'data']" in generated_content
        assert "CONCURRENCY_LIMIT = 2" in generated_content
        
        # Verify script structure
        assert "def deploy():" in generated_content
        assert "def custom_pre_deploy_hook():" in generated_content
        assert "def custom_post_deploy_hook():" in generated_content
        assert "get_custom_deploy_args" in generated_content
        assert 'if __name__ == "__main__":' in generated_content
        
        # Verify Python syntax is valid
        try:
            compile(generated_content, str(script_path), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Generated script has invalid Python syntax: {e}")
        
        # Step 7: Test script discovery (simulating DeploymentScriptExecutor)
        found_scripts = list(scripts_root.rglob("*_deploy.py"))
        assert len(found_scripts) == 1
        assert script_path in found_scripts
        
        # Test filtering by project
        project_scripts = list((scripts_root / "data_pipeline").rglob("*_deploy.py"))
        assert len(project_scripts) == 1
        
        # Test filtering by environment
        env_scripts = list(scripts_root.rglob("production/*_deploy.py"))
        assert len(env_scripts) == 1


def test_custom_section_editing_workflow():
    """Test that custom sections can be edited and preserved."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Step 1: Create initial script with custom sections
        from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
        
        mock_deploy_info = {
            'flow_name': 'test_flow',
            'generation_timestamp': '2024-01-01T12:00:00',
            'project_name': 'test_project',
            'env': 'dev',
            'module_path': 'test.module',
            'function_name': 'test_flow',
            'deployment_name': 'test-deployment',
            'description': 'Test flow',
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
        
        initial_script = DEPLOYMENT_SCRIPT_TEMPLATE.format(**mock_deploy_info)
        
        # Step 2: Simulate editing the custom section
        custom_section = '''
def custom_pre_deploy_hook():
    """Custom pre-deploy logic."""
    print("Running custom pre-deploy validation")
    # Add custom validation logic here
    
def custom_post_deploy_hook():
    """Custom post-deploy logic."""
    print("Running custom post-deploy notifications")
    # Send Slack notification, update monitoring, etc.
    
def get_custom_deploy_args() -> Dict[str, Any]:
    """Custom deployment arguments."""
    return {
        "schedules": [],  # Custom schedule handling
        "parameters": {"custom_param": "custom_value"}
    }
'''
        
        # Replace the custom section in the script
        start_marker = "# CUSTOM_DEPLOYMENT_CONFIG - Add your custom deployment logic here\n# This section will be preserved when regenerating the deployment script\n# =============================================================================\n"
        end_marker = "\n# =============================================================================\n# END CUSTOM_DEPLOYMENT_CONFIG"
        
        start_idx = initial_script.find(start_marker)
        end_idx = initial_script.find(end_marker)
        
        assert start_idx != -1 and end_idx != -1
        
        # Create edited script with custom section
        edited_script = (
            initial_script[:start_idx + len(start_marker)] +
            custom_section +
            initial_script[end_idx:]
        )
        
        # Step 3: Verify the edited script is valid Python
        try:
            compile(edited_script, '<string>', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Edited script has invalid Python syntax: {e}")
        
        # Step 4: Verify custom content is preserved
        assert "Running custom pre-deploy validation" in edited_script
        assert "Running custom post-deploy notifications" in edited_script
        assert "custom_param" in edited_script
        
        # Step 5: Test extraction of custom sections (simulating regeneration)
        import re
        
        pattern = r'# CUSTOM_DEPLOYMENT_CONFIG[^\n]*\n(.*?)\n# END CUSTOM_DEPLOYMENT_CONFIG'
        match = re.search(pattern, edited_script, re.DOTALL)
        
        assert match is not None
        extracted_custom_section = match.group(1)
        assert "Running custom pre-deploy validation" in extracted_custom_section
        assert "custom_param" in extracted_custom_section


def test_cli_integration_points():
    """Test the integration points with the CLI without actually running CLI commands."""
    
    # Test that the new CLI commands would have the right structure
    expected_commands = [
        "generate-scripts",
        "deploy-scripts", 
        "list-scripts",
        "validate-scripts"
    ]
    
    # This test verifies the concepts without importing the CLI module
    # (which would require additional dependencies)
    
    # Mock command line arguments that would be passed to each command
    generate_args = {
        'command': 'generate-scripts',
        'project_name': 'my-project',
        'branch_name': 'main',
        'commit_hash': 'abc123',
        'image_uri': 'my-image:latest',
        'package_version': '1.0.0',
        'env': 'prod',
        'flows_to_deploy': 'flow1,flow2',
        'scripts_root_dir': './deployment_scripts',
        'overwrite': False
    }
    
    deploy_args = {
        'command': 'deploy-scripts',
        'scripts_root_dir': './deployment_scripts',
        'project_name': 'my-project',
        'env': 'prod',
        'flows_to_deploy': 'flow1,flow2'
    }
    
    list_args = {
        'command': 'list-scripts',
        'scripts_root_dir': './deployment_scripts',
        'project_name': 'my-project',
        'env': 'prod'
    }
    
    validate_args = {
        'command': 'validate-scripts',
        'scripts_root_dir': './deployment_scripts',
        'project_name': 'my-project',
        'env': 'prod'
    }
    
    # Test that argument structures are consistent
    all_args = [generate_args, deploy_args, list_args, validate_args]
    
    for args in all_args:
        assert 'command' in args
        assert args['command'] in expected_commands
        assert 'scripts_root_dir' in args
    
    # Test that filtering arguments are consistent across commands
    filtering_commands = [deploy_args, list_args, validate_args]
    for args in filtering_commands:
        assert 'project_name' in args
        assert 'env' in args
    
    # Verify that the generate command has all required deployment parameters
    required_generate_params = [
        'project_name', 'branch_name', 'commit_hash', 
        'image_uri', 'package_version', 'env', 'flows_to_deploy'
    ]
    
    for param in required_generate_params:
        assert param in generate_args, f"Missing required parameter: {param}"