# acme-portal-sdk

SDK to provide data and actions for `acme-portal` `VSCode` [extension](https://github.com/blackwhitehere/acme-portal).

Rather than embedding a pre-defined logic in `acme-portal` extension, the SDK
allows to define sources of data and behaviour for extension functionality. As such, the extension servers as UI layer to the implementation provided by SDK objects.

# Problem

A repeatable source of pain while working on software is that deployment processes are highly specific to a given project. While the application may be written in a well known language or framework, the deployment process is usually specialized to a given application, team and company making it difficult for new and existing team members to understand how to just "ship" their code.

`acme-portal` and `acme-portal-sdk` attempt to address that problem by proposing a standard UI & workflow of deploying a python application.
However, rather than dictating an exact deployment implementation, the two packages jointly define only high level deployment concepts and allow users to customize the implementation.

In a way, they attempt to make the deployment process as frictionless and intuitive as possible, without simplifying the deployment to a restrained set of practices.

`acme-portal-sdk` provides a specific implementation of a deployment process for a python application based on `prefect` orchestration library, however users of the SDK can easily extend the interfaces to their projects. Some standard implementation schemes like one based on e.g. `airflow` can be made part of SDK in the future.

# Concepts

To the end of clarifying deployment process, the SDK defines the following concepts:

* `Flow` - (often named in various frameworks as `Workflow` / `Job` / `DAG`) is a unit of work in an application. It can also be though of as an `executable script` or `entrypoint`. A `Flow` can have sub-elements like `Steps` / `Tasks` / `Nodes`, but those are not tracked by the SDK. Flows form a basis of what unit of computation is deployed. In this way an application is composed of multiple related `Flows` maintained by the team, with a desire to deploy them independently of each other.
* `Deployment` - is a piece of configuration defined in an execution environment (e.g. `Prefect`/`Airflow` Server, a remote server, some AWS Resources) that defines how to run a unit of work (a `Flow`). `Deployment` is then capable of orchestrating physical resources (by e.g. submitting requests, having execute permissions) and generally use environment resources to perform computation.
* `Environment` - (sometimes called `Namespace`, `Version`, `Label`) is a persistent identifier of an application version run in a given `Deployment`. Popular `Environment` names used are `dev`, `tst`, `uat`, `prod`. Environment names are useful to communicate state of a given feature (and its code changes) in an application release cycle: "those changes are in`dev` only", "this feature needs to be tested in `uat`", etc.

Having those concepts defined the SDK defines the following actions:

* `Find Flows` - scan codebase or configration to find `Flows` which can be deployed
* `Find Deployments` - find existing `Flow` deployment information 
* `Deploy` - uses information about the `Flow` together with additional deployment configuration to create a `Deployment` in an initial, starting environment (e.g. `dev`).
* `Promote` - having completed required validation steps on deployment outputs in a given environment, the code version used in source `Deployment` can be deployed to a target environment (e.g. from `dev` to `uat`)

The `acme-portal` VSCode extension then displays flow and deployment infromation and provides UI elements (buttons) / VSCode tasks to trigger `Deploy` and `Promote` actions.

For explanation on how to configure your project to work with `acme-portal` using the SDK, checkout [Configuring SDK for your project](guides.md#configuring-sdk-for-your-project)

For explanation of the features provided by default `prefect` based implementation checkout [Default functionality of `prefect` based implementation](features.md#default-functionality-of-prefect-based-implementation)

See guide [Using default `prefect` based functionality](guides.md#using-default-prefect-based-functionality) for how to configure your project to work with `acme-portal` using the default `prefect` based implementation.


# Python environment

The project comes with a python development environment.
To generate it, after checking out the repo run:

    chmod +x create_env.sh

Then to generate the environment (or update it to latest version based on state of `uv.lock`), run:

    ./create_env.sh

This will generate a new python virtual env under `.venv` directory. You can activate it via:

    source .venv/bin/activate

If you are using VSCode, set to use this env via `Python: Select Interpreter` command.

# Project template

This project has been setup with `acme-project-create`, a python code template library.

# Required setup post use

* Enable GitHub Pages to be published via [GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow) by going to `Settings-->Pages-->Source`
* Create `release-pypi` environment for [GitHub Actions](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#creating-an-environment) to enable uploads of the library to PyPi. Set protections on what tags can deploy to this environment (Point 10). Set it to tags following pattern `v*`.
* Setup auth to PyPI for the GitHub Action implemented in `.github/workflows/release.yml` via [Trusted Publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) `uv publish` [doc](https://docs.astral.sh/uv/guides/publish/#publishing-your-package)
* Once you create the python environment for the first time add the `uv.lock` file that will be created in project directory to the source control and update it each time environment is rebuilt
* In order not to replicate documentation in `docs/docs/index.md` file and `README.md` in root of the project setup a symlink from `README.md` file to the `index.md` file.
To do this, from `docs/docs` dir run:

        ln -sf ../../README.md index.md

* Run `pre-commit install` to install the pre-commit hooks.