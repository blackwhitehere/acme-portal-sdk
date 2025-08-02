import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from acme_portal_sdk.airflow.flow_finder import AirflowFlowFinder
from acme_portal_sdk.airflow.deployment_finder import AirflowDeploymentFinder
from acme_portal_sdk.airflow.flow_deploy import AirflowFlowDeployer
from acme_portal_sdk.airflow.deployment_promote import AirflowDeploymentPromote
from acme_portal_sdk.flow_deploy import DeployInfo


class TestAirflowFlowFinder:
    """Test cases for AirflowFlowFinder."""

    def test_find_dags_traditional_instantiation(self):
        """Test finding DAGs using traditional DAG instantiation."""
        # Create a temporary file with DAG content
        dag_content = """
from airflow import DAG
from datetime import datetime

my_dag = DAG(
    dag_id="test_dag",
    description="Test DAG",
    start_date=datetime(2024, 1, 1)
)
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dag_file = os.path.join(temp_dir, "test_dag.py")
            with open(dag_file, "w") as f:
                f.write(dag_content)

            finder = AirflowFlowFinder(temp_dir)
            flows = finder.find_flows()

            assert len(flows) == 1
            flow = flows[0]
            assert flow.name == "test_dag"
            assert flow.original_name == "test_dag"
            assert flow.obj_type == "dag"
            assert flow.obj_name == "my_dag"
            assert flow.description == "Test DAG"

    def test_find_dags_decorator_style(self):
        """Test finding DAGs using @dag decorator."""
        dag_content = """
from airflow.decorators import dag
from datetime import datetime

@dag(
    dag_id="decorated_dag",
    description="Decorated DAG",
    start_date=datetime(2024, 1, 1)
)
def my_dag_function():
    pass

dag_instance = my_dag_function()
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dag_file = os.path.join(temp_dir, "decorated_dag.py")
            with open(dag_file, "w") as f:
                f.write(dag_content)

            finder = AirflowFlowFinder(temp_dir)
            flows = finder.find_flows()

            assert len(flows) == 1
            flow = flows[0]
            assert flow.name == "decorated_dag"
            assert flow.original_name == "decorated_dag"
            assert flow.obj_type == "function"
            assert flow.obj_name == "my_dag_function"
            assert flow.description == "Decorated DAG"

    def test_find_no_dags(self):
        """Test handling files with no DAGs."""
        content = """
def regular_function():
    pass

class RegularClass:
    pass
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "no_dags.py")
            with open(file_path, "w") as f:
                f.write(content)

            finder = AirflowFlowFinder(temp_dir)
            flows = finder.find_flows()

            assert len(flows) == 0


class TestAirflowDeploymentFinder:
    """Test cases for AirflowDeploymentFinder."""

    @patch("requests.request")
    def test_get_deployments_success(self, mock_request):
        """Test successful retrieval of deployments."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dags": [
                {
                    "dag_id": "acme-project--main--data-processing--dev",
                    "description": "Data processing pipeline",
                    "is_active": True,
                    "is_paused": False,
                    "tags": [
                        "PROJECT=acme-project",
                        "BRANCH=main",
                        "ENV=dev",
                        "COMMIT_HASH=abc123",
                    ],
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_parsed_time": "2024-01-02T00:00:00Z",
                    "schedule_interval": "@daily",
                    "catchup": False,
                    "max_active_runs": 1,
                    "fileloc": "/opt/airflow/dags/data_processing.py",
                    "owners": ["admin"],
                }
            ]
        }
        mock_request.return_value = mock_response

        finder = AirflowDeploymentFinder(
            airflow_url="http://localhost:8080", username="admin", password="password"
        )
        finder.credentials_verified = True  # Skip verification for test

        deployments = finder.get_deployments()

        assert len(deployments) == 1
        deployment = deployments[0]
        assert deployment.name == "acme-project--main--data-processing--dev"
        assert deployment.project_name == "acme-project"
        assert deployment.branch == "main"
        assert deployment.flow_name == "data_processing"
        assert deployment.env == "dev"
        assert deployment.commit_hash == "abc123"

    @patch("requests.request")
    def test_get_deployments_connection_error(self, mock_request):
        """Test handling of connection errors."""
        mock_request.side_effect = Exception("Connection failed")

        finder = AirflowDeploymentFinder(
            airflow_url="http://localhost:8080", username="admin", password="password"
        )

        # Connection error during initialization should result in credentials_verified=False
        assert not finder.credentials_verified

        # get_deployments should return empty list when credentials not verified
        deployments = finder.get_deployments()
        assert deployments == []


class TestAirflowFlowDeployer:
    """Test cases for AirflowFlowDeployer."""

    @patch("requests.request")
    def test_deploy_existing_dag(self, mock_request):
        """Test deploying to an existing DAG."""
        # Mock DAG exists response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        deployer = AirflowFlowDeployer(
            airflow_url="http://localhost:8080", username="admin", password="password"
        )

        deploy_info = DeployInfo(name="test_dag", flow_name="test_flow", paused=False)

        # Should not raise an exception
        deployer.deploy(deploy_info)

        # Verify API calls were made
        assert mock_request.call_count >= 1

    def test_deploy_missing_airflow_url(self):
        """Test error when AIRFLOW_URL is not set."""
        with pytest.raises(ValueError, match="AIRFLOW_URL not set"):
            AirflowFlowDeployer()


class TestAirflowDeploymentPromote:
    """Test cases for AirflowDeploymentPromote."""

    @patch("requests.request")
    def test_promote_success(self, mock_request):
        """Test successful promotion between environments."""
        # Mock responses for source and target DAG checks
        source_response = MagicMock()
        source_response.status_code = 200
        source_response.json.return_value = {
            "dag_id": "project--main--flow--dev",
            "is_paused": False,
        }

        target_response = MagicMock()
        target_response.status_code = 200
        target_response.json.return_value = {"dag_id": "project--main--flow--prod"}

        update_response = MagicMock()
        update_response.status_code = 200

        mock_request.side_effect = [source_response, target_response, update_response]

        promoter = AirflowDeploymentPromote(
            source_airflow_url="http://dev-airflow:8080",
            target_airflow_url="http://prod-airflow:8080",
            source_username="admin",
            source_password="password",
            target_username="admin",
            target_password="password",
        )

        # Should not raise an exception
        promoter.promote(
            project_name="project",
            branch_name="main",
            source_env="dev",
            target_env="prod",
            flows_to_deploy=["flow"],
        )

        # Verify correct number of API calls
        assert mock_request.call_count == 3

    def test_promote_missing_urls(self):
        """Test error when required URLs are not set."""
        with pytest.raises(ValueError, match="AIRFLOW_SOURCE_URL not set"):
            AirflowDeploymentPromote()
