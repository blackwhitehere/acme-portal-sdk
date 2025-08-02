#!/usr/bin/env python3
"""Example usage of the Airflow SDK components."""

import os
from acme_portal_sdk.airflow.flow_finder import AirflowFlowFinder
from acme_portal_sdk.airflow.deployment_finder import AirflowDeploymentFinder
from acme_portal_sdk.airflow.flow_deploy import AirflowFlowDeployer
from acme_portal_sdk.flow_deploy import DeployInfo


def main():
    """Demonstrate Airflow SDK functionality."""

    print("=== Airflow Portal SDK Demo ===\n")

    # 1. Find Airflow DAGs in code
    print("1. Finding DAGs in examples/flows directory...")
    flow_finder = AirflowFlowFinder("examples/flows")
    flows = flow_finder.find_flows()

    print(f"Found {len(flows)} DAGs:")
    for flow in flows:
        print(f"  - {flow.name} ({flow.obj_type}) in {flow.source_relative}")
        print(f"    Description: {flow.description}")
        print(f"    Import path: {flow.import_path}")
        print()

    # 2. Connect to Airflow and find existing deployments (requires Airflow to be running)
    print("2. Connecting to Airflow API to find deployments...")
    print(
        "Note: This requires AIRFLOW_URL, AIRFLOW_USERNAME, and AIRFLOW_PASSWORD environment variables"
    )

    airflow_url = os.environ.get("AIRFLOW_URL")
    if airflow_url:
        try:
            deployment_finder = AirflowDeploymentFinder()
            if deployment_finder.credentials_verified:
                deployments = deployment_finder.get_deployments()
                print(f"Found {len(deployments)} deployments:")
                for deployment in deployments:
                    print(f"  - {deployment.name}")
                    print(f"    Project: {deployment.project_name}")
                    print(f"    Branch: {deployment.branch}")
                    print(f"    Environment: {deployment.env}")
                    print(f"    Flow: {deployment.flow_name}")
                    print(f"    URL: {deployment.url}")
                    print()
            else:
                print("Could not verify Airflow credentials")
        except Exception as e:
            print(f"Error connecting to Airflow: {e}")
    else:
        print("AIRFLOW_URL not set. Skipping deployment discovery.")

    # 3. Example of deploying a DAG (requires Airflow to be running)
    print("3. Example DAG deployment configuration...")

    if flows:
        # Use the first found flow as an example
        example_flow = flows[0]
        deploy_info = DeployInfo(
            name=f"example-project--main--{example_flow.name}--dev",
            flow_name=example_flow.name,
            paused=True,  # Start paused for safety
            description=f"Deployment of {example_flow.name} to dev environment",
            tags=["PROJECT=example-project", "BRANCH=main", "ENV=dev"],
        )

        print(f"Would deploy: {deploy_info.name}")
        print(f"Flow: {deploy_info.flow_name}")
        print(f"Paused: {deploy_info.paused}")
        print(f"Description: {deploy_info.description}")
        print(f"Tags: {deploy_info.tags}")

        if airflow_url:
            try:
                deployer = AirflowFlowDeployer(
                    airflow_url=airflow_url,
                    username=username,
                    password=password
                )
                print(f"Created deployer for {airflow_url}")
                
                # Actually call deploy and check if it worked
                try:
                    deployer.deploy(deploy_info)
                    print(f"✓ Successfully deployed {deploy_info.name}")
                except Exception as deploy_error:
                    print(f"⚠ Deployment failed (expected if DAG doesn't exist): {deploy_error}")
                    
            except Exception as e:
                print(f"Could not create deployer: {e}")

    print("\n=== Demo completed ===")


if __name__ == "__main__":
    main()
