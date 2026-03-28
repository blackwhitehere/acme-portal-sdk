"""V2 deployment paradigm for Prefect flows using deployment scripts."""

import logging
from pathlib import Path
from typing import List, Optional

from acme_portal_sdk.prefect.deployment_script_executor import DeploymentScriptExecutor
from acme_portal_sdk.prefect.deployment_script_generator import DeploymentScriptGenerator
from acme_portal_sdk.prefect.flow_deploy import PrefectDeployInfo, PrefectDeployInfoPrep


class PrefectDeploymentV2Manager:
    """Manages v2 deployment paradigm using deployment scripts."""
    
    def __init__(self, scripts_root_dir: Path):
        """
        Initialize the v2 deployment manager.
        
        Args:
            scripts_root_dir: Root directory for deployment scripts
        """
        self.scripts_root_dir = Path(scripts_root_dir)
        self.generator = DeploymentScriptGenerator(scripts_root_dir)
        self.executor = DeploymentScriptExecutor(scripts_root_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_deployment_scripts(
        self,
        deploy_infos: List[PrefectDeployInfo],
        overwrite: bool = False
    ) -> List[Path]:
        """
        Generate deployment scripts from deployment info objects.
        
        Args:
            deploy_infos: List of deployment information objects
            overwrite: If True, overwrite existing scripts; if False, preserve custom sections
            
        Returns:
            List of paths to generated deployment scripts
        """
        self.logger.info(f"Generating {len(deploy_infos)} deployment scripts")
        return self.generator.generate_all_scripts(deploy_infos, overwrite=overwrite)
    
    def deploy_from_scripts(
        self,
        project_name: Optional[str] = None,
        env: Optional[str] = None,
        flow_names: Optional[List[str]] = None,
        selected_scripts: Optional[List[Path]] = None
    ) -> List[Path]:
        """
        Execute deployment scripts to deploy flows.
        
        Args:
            project_name: Filter by project name
            env: Filter by environment
            flow_names: Filter by flow names  
            selected_scripts: Specific scripts to execute
            
        Returns:
            List of paths to successfully executed scripts
        """
        self.logger.info("Executing deployment scripts")
        return self.executor.execute_scripts(
            project_name=project_name,
            env=env,
            flow_names=flow_names,
            selected_scripts=selected_scripts
        )
    
    def list_deployment_scripts(
        self,
        project_name: Optional[str] = None,
        env: Optional[str] = None,
        flow_names: Optional[List[str]] = None
    ) -> List[Path]:
        """
        List deployment scripts matching the specified criteria.
        
        Args:
            project_name: Filter by project name
            env: Filter by environment
            flow_names: Filter by flow names
            
        Returns:
            List of paths to matching deployment scripts
        """
        return self.executor.find_deployment_scripts(
            project_name=project_name,
            env=env,
            flow_names=flow_names
        )
    
    def validate_deployment_scripts(
        self,
        project_name: Optional[str] = None,
        env: Optional[str] = None,
        flow_names: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Validate deployment scripts matching the specified criteria.
        
        Args:
            project_name: Filter by project name
            env: Filter by environment
            flow_names: Filter by flow names
            
        Returns:
            List of paths to valid scripts
        """
        return self.executor.validate_all_scripts(
            project_name=project_name,
            env=env,
            flow_names=flow_names
        )
    
    def sync_deployment_scripts(
        self,
        deploy_info_prep: PrefectDeployInfoPrep,
        project_name: str,
        branch_name: str, 
        commit_hash: str,
        image_uri: str,
        package_version: str,
        env: str,
        flows_to_deploy: List[str],
        env_vars: Optional[dict] = None,
        overwrite_existing: bool = False
    ) -> List[Path]:
        """
        Generate/update deployment scripts for specified flows and environment.
        
        This method bridges v1 and v2 paradigms by using the existing
        PrefectDeployInfoPrep to generate PrefectDeployInfo objects,
        then generating deployment scripts from them.
        
        Args:
            deploy_info_prep: v1 deployment info preparation instance
            project_name: Name of the project
            branch_name: Git branch name
            commit_hash: Git commit hash
            image_uri: Docker image URI
            package_version: Package version
            env: Target environment
            flows_to_deploy: List of flow names to deploy
            env_vars: Environment variables
            overwrite_existing: Whether to overwrite existing scripts
            
        Returns:
            List of paths to generated deployment scripts
        """
        self.logger.info(f"Syncing deployment scripts for {len(flows_to_deploy)} flows")
        
        # Use v1 logic to prepare deployment info
        deploy_infos = deploy_info_prep.prep_deploy_info(
            project_name=project_name,
            branch_name=branch_name,
            commit_hash=commit_hash,
            image_uri=image_uri,
            package_version=package_version,
            env=env,
            flows_to_deploy=flows_to_deploy,
            env_vars=env_vars
        )
        
        # Generate v2 deployment scripts
        return self.generate_deployment_scripts(
            deploy_infos=deploy_infos,
            overwrite=overwrite_existing
        )


class PrefectDeploymentV2Workflow:
    """Workflow class for v2 deployment paradigm compatible with existing DeployWorkflow interface."""
    
    def __init__(self, scripts_root_dir: Path):
        """
        Initialize the v2 deployment workflow.
        
        Args:
            scripts_root_dir: Root directory for deployment scripts
        """
        self.manager = PrefectDeploymentV2Manager(scripts_root_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def run(self, *args, **kwargs) -> Optional[str]:
        """
        Execute the v2 deployment workflow.
        
        Expected kwargs:
            mode: 'generate' or 'deploy' or 'sync'
            project_name: Project name
            env: Environment
            flows_to_deploy: List of flow names
            scripts_root_dir: Override scripts root directory
            
        Returns:
            Summary message of the operation
        """
        mode = kwargs.get('mode', 'deploy')
        project_name = kwargs.get('project_name')
        env = kwargs.get('env')
        flows_to_deploy = kwargs.get('flows_to_deploy', [])
        
        # Override scripts root directory if provided
        if 'scripts_root_dir' in kwargs:
            self.manager = PrefectDeploymentV2Manager(Path(kwargs['scripts_root_dir']))
        
        try:
            if mode == 'generate':
                # Generate scripts mode requires deploy_info_prep
                deploy_info_prep = kwargs.get('deploy_info_prep')
                if not deploy_info_prep:
                    raise ValueError("deploy_info_prep required for generate mode")
                
                scripts = self.manager.sync_deployment_scripts(
                    deploy_info_prep=deploy_info_prep,
                    project_name=project_name,
                    branch_name=kwargs.get('branch_name', 'main'),
                    commit_hash=kwargs.get('commit_hash', 'latest'),
                    image_uri=kwargs.get('image_uri', ''),
                    package_version=kwargs.get('package_version', '1.0.0'),
                    env=env,
                    flows_to_deploy=flows_to_deploy,
                    env_vars=kwargs.get('env_vars'),
                    overwrite_existing=kwargs.get('overwrite_existing', False)
                )
                return f"Generated {len(scripts)} deployment scripts"
                
            elif mode == 'deploy':
                # Deploy from existing scripts
                successful_scripts = self.manager.deploy_from_scripts(
                    project_name=project_name,
                    env=env,
                    flow_names=flows_to_deploy
                )
                return f"Successfully deployed {len(successful_scripts)} flows"
                
            elif mode == 'sync':
                # Generate scripts and deploy
                deploy_info_prep = kwargs.get('deploy_info_prep')
                if not deploy_info_prep:
                    raise ValueError("deploy_info_prep required for sync mode")
                
                # Generate scripts
                scripts = self.manager.sync_deployment_scripts(
                    deploy_info_prep=deploy_info_prep,
                    project_name=project_name,
                    branch_name=kwargs.get('branch_name', 'main'),
                    commit_hash=kwargs.get('commit_hash', 'latest'),
                    image_uri=kwargs.get('image_uri', ''),
                    package_version=kwargs.get('package_version', '1.0.0'),
                    env=env,
                    flows_to_deploy=flows_to_deploy,
                    env_vars=kwargs.get('env_vars'),
                    overwrite_existing=kwargs.get('overwrite_existing', False)
                )
                
                # Deploy from scripts
                successful_scripts = self.manager.deploy_from_scripts(
                    selected_scripts=scripts
                )
                
                return f"Generated {len(scripts)} scripts and deployed {len(successful_scripts)} flows"
                
            else:
                raise ValueError(f"Unknown mode: {mode}")
                
        except Exception as e:
            self.logger.error(f"V2 deployment workflow failed: {e}")
            raise