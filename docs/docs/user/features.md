# Features

The acme-portal-sdk provides a comprehensive set of features for managing data workflows and deployments across different orchestration platforms.

## Core Capabilities

* **Flow Discovery**: Automatically discover and analyze flow definitions from your codebase
* **Deployment Management**: Deploy flows to orchestration platforms with standardized naming conventions
* **Environment Promotion**: Promote deployments between different environments (dev, staging, prod)
* **Version Tracking**: Attach version information and commit hashes to deployments for traceability
* **Multi-Platform Support**: Support for multiple workflow orchestration platforms

## Orchestration Platform Support

The SDK supports multiple workflow orchestration platforms:

* **[Prefect](prefect.md)**: Primary platform support with built-in CLI and GitHub Actions integration
* **[Airflow](airflow.md)**: Comprehensive Apache Airflow support for DAG management and deployment

## Deployment Patterns

* Standard naming convention: `{project_name}--{branch_name}--{flow_name}--{env}`
* Environment-specific configuration management
* Automated deployment through GitHub Actions
* Version-controlled deployment configurations