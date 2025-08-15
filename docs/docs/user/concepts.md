# Core Concepts

## Problem Statement

A repeatable source of pain while working on software is that deployment processes are highly specific to a given project. While the application may be written in a well known language or framework, the deployment process is usually specialized to a given application, team and company making it difficult for new and existing team members to understand how to just "ship" their code.

`acme-portal` and `acme-portal-sdk` attempt to address that problem by proposing a standard UI & workflow of deploying a python application.
However, rather than dictating an exact deployment implementation, the two packages jointly define only high level deployment concepts and allow users to customize the implementation.

In a way, they attempt to make the deployment process as frictionless and intuitive as possible, without simplifying the deployment to a restrained set of practices.

`acme-portal-sdk` contains abstract interfaces expected by the `VSCode` `acme-portal` extension. It also contains a specific implementation for a python application based on the `prefect` orchestration library. Users of the SDK can easily extend the abstract interfaces to their projects. Some standard implementation schemes like one based on e.g. `airflow` can be made part of SDK in the future.

## Core Concepts

To the end of clarifying deployment process, the SDK defines the following concepts:

* `Flow` - (often named in various frameworks as `Workflow` / `Job` / `DAG`) is a unit of work in an application. It can also be though of as an `executable script` or `entrypoint`. A `Flow` can have sub-elements like `Steps` / `Tasks` / `Nodes`, but those are not tracked by the SDK. Flows form a basis of what unit of computation is deployed. In this way an application is composed of multiple related `Flows` maintained by the team, with a desire to deploy them independently of each other.
* `Deployment` - is a piece of configuration defined in an execution environment (e.g. `Prefect`/`Airflow` Server, a remote server, some AWS Resources) that defines how to run a unit of work (a `Flow`). `Deployment` is then capable of orchestrating physical resources (by e.g. submitting requests, having execute permissions) and generally use environment resources to perform computation.
* `Environment` - (sometimes called `Namespace`, `Version`, `Label`) is a persistent identifier of an application version run in a given `Deployment`. Popular `Environment` names used are `dev`, `tst`, `uat`, `prod`. Environment names are useful to communicate release state of a given feature (and its code changes) in an application release cycle. They give meaning to statements like "those changes are in `dev` only", "this feature needs to be tested in `uat`", etc.

Having those concepts defined the SDK defines the following actions:

* `Find Flows` - scan code or configration to find `Flows` which can be deployed
* `Find Deployments` - find existing `Flow` deployment information 
* `Deploy` - uses information about the `Flow` together with additional deployment configuration to create a `Deployment` in an initial, starting environment (e.g. `dev`).
* `Promote` - having completed required validation steps on deployment outputs in a given environment, the code version used in source `Deployment` can be deployed to a target environment (e.g. from `dev` to `uat`)

The `acme-portal` VSCode extension then displays flow and deployment infromation and provides UI elements (buttons, forms) / VSCode tasks to trigger `Deploy` and `Promote` actions.

The SDK and `acme-portal` are intended to complement use of CICD pipelines in cases where deployments can not be fully automated.