"""Generates Prefect deployment scripts from deployment information (v2 paradigm)."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE
from acme_portal_sdk.prefect.flow_deploy import PrefectDeployInfo


class DeploymentScriptGenerator:
    """Generates Python deployment scripts from PrefectDeployInfo objects."""
    
    def __init__(self, scripts_root_dir: Path):
        """
        Initialize the deployment script generator.
        
        Args:
            scripts_root_dir: Root directory where deployment scripts will be stored
        """
        self.scripts_root_dir = Path(scripts_root_dir)
        self.scripts_root_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_script(self, deploy_info: PrefectDeployInfo, overwrite: bool = False) -> Path:
        """
        Generate a deployment script for the given deployment info.
        
        Args:
            deploy_info: Deployment information to generate script from
            overwrite: If True, overwrite existing script; if False, preserve custom sections
            
        Returns:
            Path to the generated deployment script
        """
        script_path = self._get_script_path(deploy_info)
        
        # If script exists and we're not overwriting, preserve custom sections
        custom_sections = {}
        if script_path.exists() and not overwrite:
            custom_sections = self._extract_custom_sections(script_path)
        
        # Generate the script content
        script_content = self._generate_script_content(deploy_info, custom_sections)
        
        # Ensure parent directory exists
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the script
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make script executable
        script_path.chmod(0o755)
        
        return script_path
    
    def _get_script_path(self, deploy_info: PrefectDeployInfo) -> Path:
        """
        Generate the path for a deployment script based on deployment info.
        
        Convention: {scripts_root_dir}/{project_name}/{env}/{flow_name}_deploy.py
        """
        # Extract project info from deployment name
        # Expected format: project_name--branch_name--flow-name--env
        name_parts = deploy_info.name.split('--')
        if len(name_parts) >= 4:
            project_name = name_parts[0]
            env = name_parts[-1]
        else:
            # Fallback if naming convention is different
            project_name = "default"
            env = "default"
        
        flow_name = deploy_info.flow_name.replace('-', '_')
        filename = f"{flow_name}_deploy.py"
        
        return self.scripts_root_dir / project_name / env / filename
    
    def _generate_script_content(self, deploy_info: PrefectDeployInfo, custom_sections: Dict[str, str]) -> str:
        """Generate the script content from deployment info and custom sections."""
        
        # Extract module and function information
        if not deploy_info.flow_function:
            raise ValueError(f"Flow function not available for {deploy_info.name}")
        
        module_path = deploy_info.flow_function.__module__
        function_name = deploy_info.flow_function.__name__
        
        # Extract project info from deployment name
        name_parts = deploy_info.name.split('--')
        project_name = name_parts[0] if len(name_parts) >= 4 else "default"
        env = name_parts[-1] if len(name_parts) >= 4 else "default"
        
        # Format template with deployment info
        script_content = DEPLOYMENT_SCRIPT_TEMPLATE.format(
            flow_name=deploy_info.flow_name,
            generation_timestamp=datetime.now().isoformat(),
            project_name=project_name,
            env=env,
            module_path=module_path,
            function_name=function_name,
            deployment_name=deploy_info.name,
            description=deploy_info.description,
            work_pool_name=deploy_info.work_pool_name,
            work_queue_name=deploy_info.work_queue_name,
            cron=deploy_info.cron,
            parameters=deploy_info.parameters,
            job_variables=deploy_info.job_variables,
            image_uri=deploy_info.image_uri,
            tags=deploy_info.tags,
            version=deploy_info.version,
            paused=deploy_info.paused,
            concurrency_limit=deploy_info.concurrency_limit,
        )
        
        # Replace custom sections if they exist
        if custom_sections:
            script_content = self._replace_custom_sections(script_content, custom_sections)
        
        return script_content
    
    def _extract_custom_sections(self, script_path: Path) -> Dict[str, str]:
        """Extract custom sections from an existing deployment script."""
        custom_sections = {}
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find custom deployment config section
            pattern = r'# CUSTOM_DEPLOYMENT_CONFIG[^\n]*\n(.*?)\n# END CUSTOM_DEPLOYMENT_CONFIG'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                custom_sections['custom_deployment_config'] = match.group(1)
        
        except Exception:
            # If we can't read the file, return empty custom sections
            pass
        
        return custom_sections
    
    def _replace_custom_sections(self, script_content: str, custom_sections: Dict[str, str]) -> str:
        """Replace custom sections in the generated script content."""
        
        if 'custom_deployment_config' in custom_sections:
            # Replace the custom deployment config section
            pattern = r'(# CUSTOM_DEPLOYMENT_CONFIG[^\n]*\n)(.*?)(\n# END CUSTOM_DEPLOYMENT_CONFIG)'
            replacement = f'\\g<1>{custom_sections["custom_deployment_config"]}\\g<3>'
            script_content = re.sub(pattern, replacement, script_content, flags=re.DOTALL)
        
        return script_content
    
    def generate_all_scripts(self, deploy_infos: List[PrefectDeployInfo], overwrite: bool = False) -> List[Path]:
        """
        Generate deployment scripts for all provided deployment infos.
        
        Args:
            deploy_infos: List of deployment information objects
            overwrite: If True, overwrite existing scripts; if False, preserve custom sections
            
        Returns:
            List of paths to generated deployment scripts
        """
        generated_scripts = []
        
        for deploy_info in deploy_infos:
            try:
                script_path = self.generate_script(deploy_info, overwrite=overwrite)
                generated_scripts.append(script_path)
                print(f"Generated deployment script: {script_path}")
            except Exception as e:
                print(f"Error generating script for {deploy_info.name}: {e}")
                raise
        
        return generated_scripts