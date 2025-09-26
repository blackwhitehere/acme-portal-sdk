#!/usr/bin/env python
"""
Demo script showing the V2 deployment paradigm in action.

This script demonstrates how the V2 system would work without requiring
Prefect to be installed, showing the generated deployment scripts.
"""

import tempfile
from pathlib import Path
from acme_portal_sdk.prefect.deployment_script_template import DEPLOYMENT_SCRIPT_TEMPLATE


def main():
    """Demonstrate the V2 deployment paradigm."""
    
    print("🚀 Prefect V2 Deployment Paradigm Demo")
    print("=" * 50)
    
    # Create a temporary directory for our demo
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        scripts_root = temp_path / "deployment_scripts"
        
        print(f"📁 Creating demo in: {scripts_root}")
        
        # Demo configuration - simulating what would come from PrefectDeployInfo
        demo_deployments = [
            {
                'flow_name': 'data_processing_flow',
                'generation_timestamp': '2024-01-15T10:30:00',
                'project_name': 'data_pipeline',
                'env': 'production',
                'module_path': 'flows.data_processing',
                'function_name': 'data_processing_flow',
                'deployment_name': 'data-pipeline--main--data-processing-flow--production',
                'description': 'Process daily data files from external sources',
                'work_pool_name': 'production-ecs-pool',
                'work_queue_name': 'high-priority',
                'cron': '0 2 * * *',  # Daily at 2 AM
                'parameters': {
                    'batch_size': 1000,
                    'retry_count': 3,
                    'source_bucket': 'prod-data-bucket'
                },
                'job_variables': {
                    'ENV': 'production',
                    'LOG_LEVEL': 'INFO',
                    'MEMORY': '4Gi',
                    'CPU': '2'
                },
                'image_uri': 'myregistry/data-processor:v1.2.0',
                'tags': ['production', 'daily', 'data-processing'],
                'version': '1.2.0',
                'paused': False,
                'concurrency_limit': 2,
            },
            {
                'flow_name': 'report_generation_flow',
                'generation_timestamp': '2024-01-15T10:30:00',
                'project_name': 'data_pipeline',
                'env': 'production',
                'module_path': 'flows.reporting',
                'function_name': 'report_generation_flow',
                'deployment_name': 'data-pipeline--main--report-generation-flow--production',
                'description': 'Generate weekly business reports',
                'work_pool_name': 'production-ecs-pool',
                'work_queue_name': 'normal-priority',
                'cron': '0 6 * * 1',  # Weekly on Monday at 6 AM
                'parameters': {
                    'report_type': 'weekly',
                    'include_charts': True
                },
                'job_variables': {
                    'ENV': 'production',
                    'LOG_LEVEL': 'INFO',
                    'MEMORY': '2Gi',
                    'CPU': '1'
                },
                'image_uri': 'myregistry/report-generator:v1.1.0',
                'tags': ['production', 'weekly', 'reporting'],
                'version': '1.1.0',
                'paused': False,
                'concurrency_limit': 1,
            }
        ]
        
        # Generate deployment scripts
        print("\n📝 Generating deployment scripts...")
        generated_scripts = []
        
        for deploy_config in demo_deployments:
            # Create project/env directory structure
            project_dir = scripts_root / deploy_config['project_name']
            env_dir = project_dir / deploy_config['env']
            env_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate script content
            script_content = DEPLOYMENT_SCRIPT_TEMPLATE.format(**deploy_config)
            
            # Write script
            script_name = f"{deploy_config['flow_name']}_deploy.py"
            script_path = env_dir / script_name
            script_path.write_text(script_content)
            script_path.chmod(0o755)  # Make executable
            
            generated_scripts.append(script_path)
            print(f"   ✅ Generated: {script_path.relative_to(temp_path)}")
        
        print(f"\n📊 Generated {len(generated_scripts)} deployment scripts")
        
        # Show directory structure
        print("\n🌳 Directory structure:")
        def show_tree(path, prefix="", is_last=True):
            if path.is_dir():
                print(f"{prefix}{'└── ' if is_last else '├── '}{path.name}/")
                children = sorted(path.iterdir())
                for i, child in enumerate(children):
                    is_last_child = i == len(children) - 1
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    show_tree(child, new_prefix, is_last_child)
            else:
                print(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")
        
        show_tree(scripts_root)
        
        # Show sample script content
        print(f"\n📄 Sample script content ({generated_scripts[0].name}):")
        print("-" * 60)
        
        sample_content = generated_scripts[0].read_text()
        # Show first 30 lines
        lines = sample_content.split('\n')
        for i, line in enumerate(lines[:30]):
            print(f"{i+1:3d}: {line}")
        
        if len(lines) > 30:
            print(f"... ({len(lines) - 30} more lines)")
        
        print("-" * 60)
        
        # Demonstrate custom section editing
        print("\n✏️  Demonstrating custom section editing...")
        
        # Find and show custom section
        custom_start = sample_content.find("# CUSTOM_DEPLOYMENT_CONFIG")
        custom_end = sample_content.find("# END CUSTOM_DEPLOYMENT_CONFIG")
        
        if custom_start != -1 and custom_end != -1:
            custom_section = sample_content[custom_start:custom_end + len("# END CUSTOM_DEPLOYMENT_CONFIG")]
            print("Custom section (user can edit this):")
            print("```python")
            for i, line in enumerate(custom_section.split('\n')[:15]):
                print(f"{i+1:2d}: {line}")
            print("```")
        
        # Show CLI usage examples
        print("\n🖥️  CLI Usage Examples:")
        print("   # Generate scripts from existing config:")
        print("   aps-prefect-deploy generate-scripts \\")
        print("     -project-name data-pipeline \\")
        print("     -branch-name main \\")
        print("     -env production \\")
        print("     --scripts-root-dir ./deployment_scripts")
        print()
        print("   # Deploy all flows for an environment:")
        print("   aps-prefect-deploy deploy-scripts \\")
        print("     --project-name data-pipeline \\")
        print("     --env production")
        print()
        print("   # List available scripts:")
        print("   aps-prefect-deploy list-scripts \\")
        print("     --env production")
        print()
        print("   # Validate scripts:")
        print("   aps-prefect-deploy validate-scripts")
        
        # Show customization examples
        print("\n🔧 Customization Examples:")
        print("   You can edit the custom sections to add:")
        print("   • Pre-deployment validation")
        print("   • Post-deployment notifications")
        print("   • Custom deployment arguments")
        print("   • Environment-specific logic")
        print("   • Integration with monitoring systems")
        
        print("\n✨ V2 Deployment Benefits:")
        print("   ✅ Full flexibility - supports any Prefect deployment argument")
        print("   ✅ Explicit configuration - all parameters visible in scripts")
        print("   ✅ Version control friendly - scripts can be committed")
        print("   ✅ Customizable - add custom deployment logic")
        print("   ✅ CI/CD ready - integrate easily with pipelines")
        print("   ✅ Backward compatible - works alongside V1 approach")
        
        print(f"\n🎉 Demo complete! Scripts were generated in: {scripts_root}")
        print("    (temporary directory - will be cleaned up)")


if __name__ == "__main__":
    main()