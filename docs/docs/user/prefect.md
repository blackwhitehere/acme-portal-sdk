# Prefect Support

The acme-portal-sdk provides built-in support for Prefect as the primary flow orchestration platform.

## Default functionality of `prefect` based implementation

Prefect based implementation has been designed for a project where a team implements multiple flows that run in a shared python environment, but want to deploy them independently.

* A standard code structure is assumed where flows are defined using the `@flow` decorator across files spread out from a source root.
* Flow names are standardized to use underscores rather than hyphens to align with expectation since flow names are often derived from python function names.
* Deployment name will be composed of a pattern `{project_name}--{branch_name}--{hyphen_flow_name}--{env}` and available to the deployed flow as an env var `DEPLOYMENT_NAME`. This should be used to make sure any persisted data is annotated with label information.
* Versioning info (`PACKAGE_VERSION` and `COMMIT_HASH`) of code used in deployment will be attached as tags to the deployment.
* `Deploy` action is implemented as a GitHub Actions Workflow under `.github/workflows/deploy.yml`. It's triggered automatically on merge to `main` branch following completion of `test.yml` and `container.yml` pipelines that run unit tests and build container image respectively. It uses [`acme-config`](https://github.com/blackwhitehere/acme-config) to retreive current set of environment variables associated with a given environment name. Then, it calls a script `aps-prefect-deploy` that that uses SDK classes (`PrefectDeployInfoPrep`, `PrefectFlowDeployer`) to perform the deployment.
* `Promote` action will extract code version used in source deployment from attached tags and set it to be used in target deployment. It will also set env vars associated with target environment in the new deployment. This way only necessary deployment elements are changed from the source deployment and every other deployment configuration which was tested in source environment is inherited in target environment. It is implemented in `promote.yml` GitHub Action.

## Built-in CLI for prefect based deployment

`acme-portal-sdk` ships with a built in CLI command `aps-prefect-deploy` that implements `deploy` and `promote` commands using SDK classes.

Specifically `PrefectDeployInfoPrep` is used to load a static config file of deployment related configuration and use it as part of deployment information. `PrefectFlowDeployer` is also used to execute the deployment.

For more info run:

    aps-prefect-deploy --help