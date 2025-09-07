# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **PrefectFlowAttributes Simplification**: Removed `obj_type`, `obj_parent_type`, and `obj_parent` attributes from PrefectFlowAttributes dataclass as they were not useful. The `obj_name` attribute is kept in PrefectFlowAttributes as it's required for deployment functionality. This reduces the captured metadata to essential attributes: `obj_name`, `module`, and `import_path` (#35)

### Fixed
- **Release Notes Validation**: Enhanced release notes check script to handle merge conflicts and provide better error messages in CI environments (#33)

## [1.1.3alpha1] - 2025-08-29

### Fixed
- **Import error** Fixed import error (fc30d1e)

## [1.1.2alpha1] - 2025-08-29

### Fixed
- **Serializable call args** Fixed type casting for __call__ method (90becf3)

## [1.1.1alpha2] - 2025-08-29

### Fixed
- **Fix unupdated call method in ABCs after method signature change** Fixed interface bug (63ade61)

## [1.1.0alpha1] - 2025-08-29

### Added
- **Selective Re-fetching Support**: Added optional parameters `flows_to_fetch` and `flow_groups` to FlowFinder.find_flows method, and `deployments_to_fetch` and `flows_to_fetch` to DeploymentFinder.get_deployments method for selective data re-fetching instead of full scans (#30)

### Fixed
- **Release Notes Check Context Awareness**: Modified test.yml GitHub Actions workflow to run release notes validation context-appropriately - validates specific PR reference for PRs, general format validation for pushes to main (#33)

## [1.0.0alpha1] - 2025-08-15

### Added
- **PrefectFlowAttributes Dataclass**: Created structured dataclass for Prefect-specific flow attributes with comprehensive documentation of each field (#27)
- **API Changes Documentation**: Added comprehensive section explaining FlowDetails v1.0.0 architectural changes, benefits, and impact (#27)

### Changed
- **Documentation Simplification**: Removed CustomFlowDetails and CustomDeploymentDetails examples from user guides, replaced with simpler implementations using base classes with child_attributes (#27)

## [1.0.0] - 2025-01-21

### Changed
- **BREAKING: FlowDetails API Simplification**: Removed `obj_type`, `obj_name`, `obj_parent_type`, `obj_parent`, `module`, and `import_path` as required attributes from FlowDetails base class. These implementation-specific attributes are now stored in `child_attributes` for Prefect and Airflow implementations. This allows for a more flexible base class while maintaining backward compatibility for specific implementations. See migration guide in user documentation for details (#27)

### Added
- **Line Number Property**: Added `line_number` field to FlowDetails for editor integration to open source files at specific line numbers (#25)
- **Release Notes Process**: Standardized release notes workflow with automated validation and extraction (#17)
- **Automated CHANGELOG.md Updates**: Release workflow now automatically updates CHANGELOG.md after publishing by moving [Unreleased] content to versioned sections (#17)

### Changed
- **Documentation Reorganization**: Moved Prefect implementation details from user guides to dedicated Prefect page for better organization (#22)
- **Enhanced Custom Implementation Guide**: Expanded "Creating Custom Workflow Implementations" section to include comprehensive examples for all four base classes (FlowFinder, DeploymentFinder, DeployWorkflow, PromoteWorkflow) with sample data and functionality (#22)
- **README.md Reorganization**: Moved Problem and Concepts sections to user documentation, added minimal showcase, and created CONTRIBUTING.md as source of truth for development practices (#21)

## Historical Releases

*Historical versions before release notes standardization. See git history for detailed changes.*

### [0.0.13] - 2024-08-11
- Multiple improvements and features
- Enhanced SDK functionality
- Documentation updates
- See git history for detailed changes

### [0.0.12] and earlier
- Initial development and feature implementations
- Core SDK functionality
- See git history for detailed changes
