# Prefect V2 Deployment Paradigm

The V2 deployment paradigm offers a flexible, script-based approach to deploying Prefect flows that addresses the limitations of the traditional V1 approach.

## Overview

### V1 vs V2 Comparison

**V1 Approach (Traditional)**
- Uses `PrefectDeployInfo` objects with embedded configuration
- Deploys via `PrefectFlowDeployer.deploy()` method
- Limited to pre-defined deployment parameters
- Difficult to customize for unique deployment requirements

**V2 Approach (Script-Based)**
- Generates executable Python deployment scripts from templates
- All deployment parameters are explicit in script code
- Fully customizable and editable by developers
- Supports advanced deployment scenarios through custom code

## Key Features

### 🎯 **Explicit Configuration**
All deployment parameters are visible and editable in generated Python scripts.

### 🔧 **Full Customization**
Add custom pre/post deployment hooks and deployment arguments.

### 📁 **Conventional Structure**
Scripts are organized by project and environment: `{project}/{env}/{flow}_deploy.py`

### 🔄 **Regeneration Safe**
Custom sections are preserved when regenerating scripts.

### 🚀 **CI/CD Ready**
Perfect for automated deployment pipelines with version control.

## Getting Started

### 1. Generate Deployment Scripts

Generate deployment scripts for your flows:

```bash
aps-prefect-deploy generate-scripts \
  -project-name my-project \
  -branch-name main \
  -commit-hash abc123 \
  -image-uri my-registry/app:1.0.0 \
  -package-version 1.0.0 \
  -env production \
  -app-name my-app \
  -ver-number 1.0.0 \
  -static-flow-config-path ./flow-config.yaml \
  --flows-to-deploy flow1,flow2 \
  --scripts-root-dir ./deployment_scripts
```

This creates scripts like:
```
deployment_scripts/
  my-project/
    production/
      flow1_deploy.py
      flow2_deploy.py
```

### 2. Review and Customize Scripts

Each generated script contains:

```python
#!/usr/bin/env python
"""
Auto-generated Prefect deployment script for flow1
Generated on: 2024-01-15T10:30:00
Project: my-project
Environment: production
"""

# Standard deployment configuration
DEPLOYMENT_NAME = "my-project--main--flow1--production"
WORK_POOL_NAME = "production-pool"
CRON = "0 2 * * *"
PARAMETERS = {"batch_size": 1000}
# ... more configuration

# =============================================================================
# CUSTOM_DEPLOYMENT_CONFIG - Add your custom deployment logic here
# =============================================================================

def custom_pre_deploy_hook():
    """Custom logic to run before deployment."""
    pass

def custom_post_deploy_hook():
    """Custom logic to run after deployment."""
    pass

def get_custom_deploy_args():
    """Return additional arguments to pass to flow_function.deploy()."""
    return {}

# =============================================================================
# END CUSTOM_DEPLOYMENT_CONFIG
# =============================================================================

def deploy():
    """Deploy the flow with the configured parameters."""
    # ... deployment logic
```

### 3. Add Custom Logic

Edit the custom sections to add your specific requirements:

```python
def custom_pre_deploy_hook():
    """Validate deployment environment."""
    print("🔍 Validating production environment...")
    # Add validation logic
    
def custom_post_deploy_hook():
    """Send deployment notifications."""
    print("📧 Sending deployment notification...")
    # Send Slack message, update monitoring, etc.
    
def get_custom_deploy_args():
    """Custom deployment arguments."""
    return {
        "schedules": [],  # Custom schedule handling
        "triggers": custom_triggers,  # Advanced trigger configuration
    }
```

### 4. Deploy from Scripts

Deploy all flows for an environment:

```bash
aps-prefect-deploy deploy-scripts \
  --scripts-root-dir ./deployment_scripts \
  --project-name my-project \
  --env production
```

Deploy specific flows:

```bash
aps-prefect-deploy deploy-scripts \
  --scripts-root-dir ./deployment_scripts \
  --flows-to-deploy flow1,flow2
```

## Script Management

### List Available Scripts

```bash
aps-prefect-deploy list-scripts \
  --scripts-root-dir ./deployment_scripts \
  --project-name my-project \
  --env production
```

### Validate Scripts

```bash
aps-prefect-deploy validate-scripts \
  --scripts-root-dir ./deployment_scripts \
  --project-name my-project
```

## Advanced Usage

### Custom Deployment Arguments

The V2 paradigm supports any argument that Prefect's `flow.deploy()` method accepts:

```python
def get_custom_deploy_args():
    return {
        "schedules": [IntervalSchedule(interval=timedelta(hours=6))],
        "triggers": [
            DeploymentEventTrigger(
                expect={"prefect.flow-run.Completed"},
                match_related={"prefect.resource.id": "prefect.flow-run.*"}
            )
        ],
        "pull_steps": [
            {"prefect.deployments.steps.git_clone_project": {
                "repository": "https://github.com/my-org/my-repo.git"
            }}
        ],
        "entrypoint": "custom/entrypoint.py:my_flow"
    }
```

### Environment-Specific Configuration

Different environments can have different deployment logic:

```python
def custom_pre_deploy_hook():
    """Environment-specific pre-deployment logic."""
    if ENV == "production":
        # Production-specific validation
        validate_production_readiness()
    elif ENV == "staging":
        # Staging-specific setup
        setup_staging_resources()
```

### Integration with CI/CD

The script-based approach works seamlessly with CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Generate deployment scripts
  run: |
    aps-prefect-deploy generate-scripts \
      -project-name ${{ github.event.repository.name }} \
      -branch-name ${{ github.ref_name }} \
      -commit-hash ${{ github.sha }} \
      # ... other parameters

- name: Commit new scripts
  run: |
    git add deployment_scripts/
    git commit -m "Update deployment scripts" || exit 0
    git push

- name: Deploy to production
  run: |
    aps-prefect-deploy deploy-scripts \
      --env production
```

## Migration from V1

The V2 paradigm is fully compatible with existing V1 configurations. You can:

1. **Keep V1 for existing deployments**: Continue using `aps-prefect-deploy deploy`
2. **Migrate gradually**: Use `generate-scripts` to create V2 scripts from V1 config
3. **Mix approaches**: Use V1 for simple deployments, V2 for complex ones

### Migration Steps

1. Generate V2 scripts from existing V1 config:
   ```bash
   aps-prefect-deploy generate-scripts [your-existing-args]
   ```

2. Review and test generated scripts

3. Customize scripts as needed

4. Switch CI/CD to use `deploy-scripts` command

5. Commit scripts to version control

## Best Practices

### ✅ **Do**
- Commit deployment scripts to version control
- Use meaningful commit messages when scripts change
- Test scripts in development environments first
- Add custom validation in `custom_pre_deploy_hook()`
- Use environment variables for sensitive configuration

### ❌ **Don't**
- Edit generated configuration sections (they'll be overwritten)
- Put secrets directly in scripts (use environment variables)
- Skip testing after customizing scripts
- Forget to validate scripts after manual edits

## Troubleshooting

### Script Generation Issues

**Problem**: Import errors in generated scripts
```bash
ModuleNotFoundError: No module named 'my.flow.module'
```

**Solution**: Ensure your flow modules are properly importable and the Python path is correct in the script.

### Deployment Failures

**Problem**: Custom deployment arguments not recognized
```bash
TypeError: deploy() got an unexpected keyword argument 'custom_arg'
```

**Solution**: Verify that custom arguments are supported by Prefect's `flow.deploy()` method.

### Script Validation

**Problem**: Script validation fails
```bash
❌ Script missing required 'deploy' function
```

**Solution**: Ensure the script hasn't been accidentally corrupted and contains the `deploy()` function.

## API Reference

### CLI Commands

| Command | Description |
|---------|-------------|
| `generate-scripts` | Generate deployment scripts from V1 configuration |
| `deploy-scripts` | Execute deployment scripts to deploy flows |
| `list-scripts` | List available deployment scripts |
| `validate-scripts` | Validate deployment script syntax and structure |

### Script Structure

| Section | Purpose | Editable |
|---------|---------|----------|
| Header comment | Script metadata | No |
| Import statements | Module imports | No |
| Configuration constants | Deployment parameters | No |
| Custom sections | User customization | Yes |
| `deploy()` function | Main deployment logic | No |

## Examples

See the [examples directory](../examples) for complete working examples of V2 deployment scripts and configurations.