"""Template for generating Prefect deployment scripts (v2 paradigm)."""

DEPLOYMENT_SCRIPT_TEMPLATE = '''#!/usr/bin/env python
"""
Auto-generated Prefect deployment script for {flow_name}
Generated on: {generation_timestamp}
Project: {project_name}
Environment: {env}

This script can be edited to customize deployment parameters.
Re-running the generator will preserve manual edits in the CUSTOM_DEPLOYMENT_CONFIG section.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to Python path to enable imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from {module_path} import {function_name} as flow_function
except ImportError as e:
    print(f"Error importing flow function: {{e}}")
    print(f"Make sure the module '{{module_path}}' and function '{{function_name}}' exist")
    sys.exit(1)

# =============================================================================
# DEPLOYMENT CONFIGURATION
# These values were generated from your deployment configuration.
# You can modify them as needed for custom deployment requirements.
# =============================================================================

DEPLOYMENT_NAME = "{deployment_name}"
DESCRIPTION = {description!r}
WORK_POOL_NAME = {work_pool_name!r}
WORK_QUEUE_NAME = {work_queue_name!r}
CRON = {cron!r}
PARAMETERS = {parameters!r}
JOB_VARIABLES = {job_variables!r}
IMAGE_URI = {image_uri!r}
TAGS = {tags!r}
VERSION = {version!r}
PAUSED = {paused!r}
CONCURRENCY_LIMIT = {concurrency_limit!r}

# =============================================================================
# CUSTOM_DEPLOYMENT_CONFIG - Add your custom deployment logic here
# This section will be preserved when regenerating the deployment script
# =============================================================================

def custom_pre_deploy_hook():
    """Custom logic to run before deployment."""
    pass

def custom_post_deploy_hook():
    """Custom logic to run after deployment."""
    pass

def get_custom_deploy_args() -> Dict[str, Any]:
    """Return additional arguments to pass to flow_function.deploy()."""
    return {{}}

# =============================================================================
# END CUSTOM_DEPLOYMENT_CONFIG
# =============================================================================

def deploy():
    """Deploy the flow with the configured parameters."""
    print(f"Deploying flow: {{DEPLOYMENT_NAME}}")
    
    # Run custom pre-deploy hook
    custom_pre_deploy_hook()
    
    try:
        # Prepare deployment arguments
        deploy_args = {{
            "name": DEPLOYMENT_NAME,
            "description": DESCRIPTION,
            "work_pool_name": WORK_POOL_NAME,
            "work_queue_name": WORK_QUEUE_NAME,
            "cron": CRON,
            "parameters": PARAMETERS,
            "job_variables": JOB_VARIABLES,
            "image": IMAGE_URI,
            "tags": TAGS,
            "version": VERSION,
            "paused": PAUSED,
            "concurrency_limit": CONCURRENCY_LIMIT,
            "build": False,
            "push": False,
        }}
        
        # Add custom deployment arguments
        custom_args = get_custom_deploy_args()
        deploy_args.update(custom_args)
        
        # Remove None values to avoid passing them to Prefect
        deploy_args = {{k: v for k, v in deploy_args.items() if v is not None}}
        
        # Deploy the flow
        deployment = flow_function.deploy(**deploy_args)
        
        print(f"Successfully deployed: {{DEPLOYMENT_NAME}}")
        print(f"Deployment ID: {{deployment.id if hasattr(deployment, 'id') else 'N/A'}}")
        
        # Run custom post-deploy hook
        custom_post_deploy_hook()
        
        return deployment
        
    except Exception as e:
        print(f"Error deploying flow {{DEPLOYMENT_NAME}}: {{e}}")
        raise

if __name__ == "__main__":
    deploy()
'''