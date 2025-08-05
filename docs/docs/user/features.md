# Features

`acme-portal-sdk` helps to manage deployments for applications that implement "flows" (Jobs/DAGs/Workflows). It's intended to be used with `acme-portal` VSCode extension.

## Core Capabilities

* **Flow Discovery**: Automatically discover and analyze flow definitions from your codebase
* **Deployment Management**: Deploy flows to orchestration platforms with standardized naming conventions
* **Environment Promotion**: Promote deployments between different environments (e.g. dev, staging, prod)
* **Version Tracking**: Attach version information and commit hashes to deployments for traceability
* **Multi-Platform Support**: Support for multiple workflow orchestration: [Prefect](prefect.md) & [Airflow](airflow.md) & CICD platforms: GitHub Actions