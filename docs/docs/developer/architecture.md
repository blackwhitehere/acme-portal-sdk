# Architecture

The main functions of `acme-portal` are:

* Displaying a list of existing `Flows` in a project
* Fetching and displaying deployment information for each `Flow`
* Providing a VSCode command & button for creating a deployment of a flow
* Providing a VSCode command & button for promoting a deployment from a source to target environment.

The data for first two are provided by calls to configured instances of:

* `FlowFinder.find_flows`
* `DeploymentFinder.get_deployments`

The actions of last two are performed by calling:

* `DeployWorkflow.run`
* `PromoteWorkflow.run`

The implementation of those base classes can be provided and configured by user in their project. Moreover, the `acme-portal-sdk` package provides concrete implementation of all of those classes for a python project based on `prefect` and using GitHub Actions for CICD.

For explanation on how to configure your project to work with `acme-portal` using the SDK, checkout [Configuring SDK for your project](../user/user-guides.md#configuring-sdk-for-your-project)

For explanation of the features provided by default `prefect` based implementation checkout [Default functionality of prefect based implementation](../user/prefect.md#default-functionality-of-prefect-based-implementation)