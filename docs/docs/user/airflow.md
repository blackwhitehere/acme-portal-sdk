# Airflow Support

The acme-portal-sdk includes built-in support for using Apache Airflow as a source of flow definitions and as a backend for fetching existing deployments.

NOTE: Since deployment of Airflow DAGs varies based on exact Airflow setup `AirflowFlowDeployer` and `AirflowDeploymentPromote` implementations are shown for interface demonstration pruposes and you should provide an implementation specific for your airflow deployment.

## Installation

To use the Airflow functionality, install the SDK with the airflow extra:

```bash
pip install acme-portal-sdk[airflow]
```

This will install the required dependencies including `apache-airflow>=3.0.0` and `requests`.

## Components

The Airflow support includes the following components:

### AirflowFlowFinder

Scans Python code directories to identify Airflow DAGs by analyzing:
- Traditional DAG instantiations (`my_dag = DAG(...)`)
- Decorator-style DAGs (`@dag def my_dag(): ...`)

```python
from acme_portal_sdk.airflow.flow_finder import AirflowFlowFinder

finder = AirflowFlowFinder("path/to/dags")
flows = finder.find_flows()
```

### AirflowDeploymentFinder

Connects to Airflow's REST API to discover and retrieve information about existing DAGs:

```python
from acme_portal_sdk.airflow.deployment_finder import AirflowDeploymentFinder

finder = AirflowDeploymentFinder(
    airflow_url="http://localhost:8080",
    username="admin",
    password="password"
)
deployments = finder.get_deployments()
```

Environment variables can also be used:
- `AIRFLOW_URL`: Base URL for Airflow webserver
- `AIRFLOW_USERNAME`: Username for basic auth
- `AIRFLOW_PASSWORD`: Password for basic auth

### AirflowFlowDeployer

Deploys flows to Airflow by updating DAG configuration.
Note: Provided for interface demonstration purposes. You need to provide your own implementation specific to your Airflow setup.

```python
from acme_portal_sdk.airflow.flow_deploy import AirflowFlowDeployer
from acme_portal_sdk.flow_deploy import DeployInfo

deployer = AirflowFlowDeployer(
    airflow_url="http://localhost:8080",
    username="admin", 
    password="password"
)

deploy_info = DeployInfo(
    name="my_dag",
    flow_name="my_flow",
    paused=False
)

deployer.deploy(deploy_info)
```

### AirflowDeploymentPromote

Promotes DAGs between different Airflow environments.
Note: Provided for interface demonstration purposes. You need to provide your own implementation specific to your Airflow setup.

```python
from acme_portal_sdk.airflow.deployment_promote import AirflowDeploymentPromote

promoter = AirflowDeploymentPromote(
    source_airflow_url="http://dev-airflow:8080",
    target_airflow_url="http://prod-airflow:8080",
    source_username="admin",
    source_password="password",
    target_username="admin",
    target_password="password"
)

promoter.promote(
    project_name="my-project",
    branch_name="main", 
    source_env="dev",
    target_env="prod",
    flows_to_deploy=["my_flow"]
)
```

## DAG Naming Convention

The Airflow integration works with DAGs that follow this naming convention:

```
{project_name}--{branch}--{flow_name}--{environment}
```

For example: `acme-project--main--data-processing--dev`

This allows the system to automatically extract project, branch, flow, and environment information from the DAG ID.

## Environment Variables

The following environment variables can be used for configuration:

- `AIRFLOW_URL`: Base URL for Airflow webserver
- `AIRFLOW_USERNAME`: Username for basic auth
- `AIRFLOW_PASSWORD`: Password for basic auth
- `AIRFLOW_SOURCE_URL`: Source Airflow URL for promotions
- `AIRFLOW_TARGET_URL`: Target Airflow URL for promotions
- `AIRFLOW_SOURCE_USERNAME`: Source username for promotions
- `AIRFLOW_SOURCE_PASSWORD`: Source password for promotions
- `AIRFLOW_TARGET_USERNAME`: Target username for promotions
- `AIRFLOW_TARGET_PASSWORD`: Target password for promotions

## Example Usage

See `examples/airflow_demo.py` for a complete example of using all Airflow components together.

## Supported Airflow Versions

This implementation is designed for Apache Airflow 3.0+ and uses the REST API endpoints. It should also work with Airflow 2.x versions that support the same API endpoints.