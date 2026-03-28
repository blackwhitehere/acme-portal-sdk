"""Scans and executes Prefect deployment scripts (v2 paradigm)."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Set


class DeploymentScriptExecutor:
    """Scans for and executes Prefect deployment scripts."""
    
    def __init__(self, scripts_root_dir: Path):
        """
        Initialize the deployment script executor.
        
        Args:
            scripts_root_dir: Root directory containing deployment scripts
        """
        self.scripts_root_dir = Path(scripts_root_dir)
    
    def find_deployment_scripts(
        self, 
        project_name: Optional[str] = None,
        env: Optional[str] = None,
        flow_names: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Find deployment scripts matching the specified criteria.
        
        Args:
            project_name: Filter by project name (directory name)
            env: Filter by environment (subdirectory name)
            flow_names: Filter by flow names (script filename prefix)
            
        Returns:
            List of paths to matching deployment scripts
        """
        if not self.scripts_root_dir.exists():
            return []
        
        scripts = []
        
        # Determine project directories to scan
        if project_name:
            project_dirs = [self.scripts_root_dir / project_name]
            if not project_dirs[0].exists():
                return []
        else:
            project_dirs = [d for d in self.scripts_root_dir.iterdir() if d.is_dir()]
        
        for project_dir in project_dirs:
            # Determine environment directories to scan
            if env:
                env_dirs = [project_dir / env]
                if not env_dirs[0].exists():
                    continue
            else:
                env_dirs = [d for d in project_dir.iterdir() if d.is_dir()]
            
            for env_dir in env_dirs:
                # Find deployment scripts in environment directory
                for script_path in env_dir.glob("*_deploy.py"):
                    # Filter by flow names if specified
                    if flow_names:
                        script_flow_name = script_path.stem.replace('_deploy', '')
                        if script_flow_name not in flow_names:
                            continue
                    
                    scripts.append(script_path)
        
        return sorted(scripts)
    
    def execute_script(self, script_path: Path) -> bool:
        """
        Execute a single deployment script.
        
        Args:
            script_path: Path to the deployment script to execute
            
        Returns:
            True if execution was successful, False otherwise
        """
        try:
            print(f"Executing deployment script: {script_path}")
            
            # Execute the script as a subprocess to ensure clean environment
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Print stdout
            if result.stdout:
                print(result.stdout)
            
            # Print stderr if there's an error
            if result.stderr:
                print(f"Script stderr: {result.stderr}", file=sys.stderr)
            
            if result.returncode == 0:
                print(f"✅ Successfully executed: {script_path}")
                return True
            else:
                print(f"❌ Script failed with return code {result.returncode}: {script_path}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Script execution timed out: {script_path}")
            return False
        except Exception as e:
            print(f"❌ Error executing script {script_path}: {e}")
            return False
    
    def execute_scripts(
        self,
        project_name: Optional[str] = None,
        env: Optional[str] = None,
        flow_names: Optional[List[str]] = None,
        selected_scripts: Optional[List[Path]] = None
    ) -> List[Path]:
        """
        Execute deployment scripts matching the specified criteria.
        
        Args:
            project_name: Filter by project name
            env: Filter by environment
            flow_names: Filter by flow names
            selected_scripts: Specific scripts to execute (overrides other filters)
            
        Returns:
            List of paths to successfully executed scripts
        """
        if selected_scripts:
            scripts_to_execute = selected_scripts
        else:
            scripts_to_execute = self.find_deployment_scripts(
                project_name=project_name,
                env=env,
                flow_names=flow_names
            )
        
        if not scripts_to_execute:
            print("No deployment scripts found matching the criteria")
            return []
        
        print(f"Found {len(scripts_to_execute)} deployment scripts to execute")
        
        successful_scripts = []
        failed_scripts = []
        
        for script_path in scripts_to_execute:
            if self.execute_script(script_path):
                successful_scripts.append(script_path)
            else:
                failed_scripts.append(script_path)
        
        # Print summary
        print(f"\n📊 Execution Summary:")
        print(f"   ✅ Successful: {len(successful_scripts)}")
        print(f"   ❌ Failed: {len(failed_scripts)}")
        
        if failed_scripts:
            print("\n❌ Failed scripts:")
            for script in failed_scripts:
                print(f"   - {script}")
        
        return successful_scripts
    
    def validate_script(self, script_path: Path) -> bool:
        """
        Validate that a deployment script can be imported and has required functions.
        
        Args:
            script_path: Path to the deployment script to validate
            
        Returns:
            True if script is valid, False otherwise
        """
        try:
            # Load the script as a module
            spec = importlib.util.spec_from_file_location("deployment_script", script_path)
            if spec is None or spec.loader is None:
                print(f"❌ Cannot load script: {script_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for required deploy function
            if not hasattr(module, 'deploy'):
                print(f"❌ Script missing required 'deploy' function: {script_path}")
                return False
            
            print(f"✅ Script validation passed: {script_path}")
            return True
            
        except Exception as e:
            print(f"❌ Script validation failed for {script_path}: {e}")
            return False
    
    def validate_all_scripts(
        self,
        project_name: Optional[str] = None,
        env: Optional[str] = None,
        flow_names: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Validate all deployment scripts matching the specified criteria.
        
        Args:
            project_name: Filter by project name
            env: Filter by environment  
            flow_names: Filter by flow names
            
        Returns:
            List of paths to valid scripts
        """
        scripts = self.find_deployment_scripts(
            project_name=project_name,
            env=env, 
            flow_names=flow_names
        )
        
        valid_scripts = []
        
        for script_path in scripts:
            if self.validate_script(script_path):
                valid_scripts.append(script_path)
        
        return valid_scripts