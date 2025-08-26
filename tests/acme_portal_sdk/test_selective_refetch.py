"""Tests for selective re-fetching functionality in FlowFinder and DeploymentFinder."""

import pytest
from unittest.mock import Mock, patch
from acme_portal_sdk.flow_finder import FlowDetails
from acme_portal_sdk.deployment_finder import DeploymentDetails
from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder
from acme_portal_sdk.airflow.flow_finder import AirflowFlowFinder

# Import deployment finders conditionally to avoid import errors when optional dependencies are missing
try:
    from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

try:
    from acme_portal_sdk.airflow.deployment_finder import AirflowDeploymentFinder
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False


class TestFlowFinderSelectiveRefetch:
    """Test selective re-fetching functionality for FlowFinder implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.flow1 = FlowDetails(
            name="flow1",
            original_name="flow-1",
            description="First flow",
            id="flow1_id",
            source_path="/path/to/flow1.py",
            source_relative="flow1.py",
            grouping=["group1"]
        )
        
        self.flow2 = FlowDetails(
            name="flow2", 
            original_name="flow-2",
            description="Second flow",
            id="flow2_id",
            source_path="/path/to/flow2.py",
            source_relative="flow2.py",
            grouping=["group2"]
        )
        
        self.flow3 = FlowDetails(
            name="flow3",
            original_name="flow-3", 
            description="Third flow",
            id="flow3_id",
            source_path="/path/to/flow3.py",
            source_relative="flow3.py",
            grouping=["group1"]
        )

    def test_prefect_flow_finder_default_behavior(self, tmp_path):
        """Test that default behavior (no parameters) works as before."""
        finder = PrefectFlowFinder(str(tmp_path))
        
        # Mock _scan_directory to return our test flows
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2,
            "flow3_id": self.flow3
        }
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            result = finder.find_flows()
            
        assert len(result) == 3
        flow_names = {f.name for f in result}
        assert flow_names == {"flow1", "flow2", "flow3"}

    def test_prefect_flow_finder_flows_to_fetch(self, tmp_path):
        """Test selective re-fetching by flows_to_fetch parameter."""
        finder = PrefectFlowFinder(str(tmp_path))
        
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2, 
            "flow3_id": self.flow3
        }
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            # Only fetch flow1 and flow3 (using name + source_relative for matching)
            result = finder.find_flows(flows_to_fetch=[self.flow1, self.flow3])
            
        assert len(result) == 2
        flow_names = {f.name for f in result}
        assert flow_names == {"flow1", "flow3"}

    def test_prefect_flow_finder_flow_groups(self, tmp_path):
        """Test selective re-fetching by flow_groups parameter."""
        finder = PrefectFlowFinder(str(tmp_path))
        
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2,
            "flow3_id": self.flow3
        }
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            # Only fetch flows from group1
            result = finder.find_flows(flow_groups=["group1"])
            
        assert len(result) == 2
        flow_names = {f.name for f in result}
        assert flow_names == {"flow1", "flow3"}

    def test_prefect_flow_finder_combined_parameters(self, tmp_path):
        """Test using both flows_to_fetch and flow_groups parameters."""
        finder = PrefectFlowFinder(str(tmp_path))
        
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2,
            "flow3_id": self.flow3
        }
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            # Fetch flow2 specifically AND all flows from group1 (should get flow1, flow2, flow3)
            result = finder.find_flows(flows_to_fetch=[self.flow2], flow_groups=["group1"])
            
        assert len(result) == 3
        flow_names = {f.name for f in result}
        assert flow_names == {"flow1", "flow2", "flow3"}

    def test_airflow_flow_finder_flows_to_fetch(self, tmp_path):
        """Test that AirflowFlowFinder also supports selective re-fetching."""
        finder = AirflowFlowFinder(str(tmp_path))
        
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2,
            "flow3_id": self.flow3
        }
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            result = finder.find_flows(flows_to_fetch=[self.flow1])
            
        assert len(result) == 1
        assert result[0].name == "flow1"


class TestDeploymentFinderSelectiveRefetch:
    """Test selective re-fetching functionality for DeploymentFinder implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        # Prefect deployment fixtures (use UUID-style IDs)
        self.prefect_deployment1 = DeploymentDetails(
            name="project1--main--flow1--dev",
            project_name="project1",
            branch="main",
            flow_name="flow1",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1"],
            id="deploy1_id",  # Prefect uses UUID-style IDs
            created_at="2023-01-01",
            updated_at="2023-01-01",
            flow_id="flow1_id",
            url="http://example.com/deploy1"
        )
        
        self.prefect_deployment2 = DeploymentDetails(
            name="project1--main--flow2--dev",
            project_name="project1", 
            branch="main",
            flow_name="flow2",
            env="dev",
            commit_hash="def456",
            package_version="1.0.0",
            tags=["tag2"],
            id="deploy2_id",  # Prefect uses UUID-style IDs
            created_at="2023-01-01",
            updated_at="2023-01-01",
            flow_id="flow2_id",
            url="http://example.com/deploy2"
        )
        
        # Airflow deployment fixtures (use DAG ID as deployment ID)
        self.airflow_deployment1 = DeploymentDetails(
            name="project1--main--flow1--dev",
            project_name="project1",
            branch="main",
            flow_name="flow1",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1"],
            id="project1--main--flow1--dev",  # Airflow uses DAG ID as deployment ID
            created_at="2023-01-01",
            updated_at="2023-01-01",
            flow_id="project1--main--flow1--dev",
            url="http://example.com/deploy1"
        )
        
        self.airflow_deployment2 = DeploymentDetails(
            name="project1--main--flow2--dev",
            project_name="project1", 
            branch="main",
            flow_name="flow2",
            env="dev",
            commit_hash="def456",
            package_version="1.0.0",
            tags=["tag2"],
            id="project1--main--flow2--dev",  # Airflow uses DAG ID as deployment ID
            created_at="2023-01-01",
            updated_at="2023-01-01",
            flow_id="project1--main--flow2--dev",
            url="http://example.com/deploy2"
        )
        
        self.flow1 = FlowDetails(
            name="flow1",
            original_name="flow-1",
            description="First flow",
            id="flow1_id",
            source_path="/path/to/flow1.py",
            source_relative="flow1.py"
        )
        
        self.flow2 = FlowDetails(
            name="flow2",
            original_name="flow-2", 
            description="Second flow",
            id="flow2_id",
            source_path="/path/to/flow2.py",
            source_relative="flow2.py"
        )

    @pytest.mark.skipif(not PREFECT_AVAILABLE, reason="Prefect not available")
    @patch('acme_portal_sdk.prefect.deployment_finder.get_client')
    def test_prefect_deployment_finder_default_behavior(self, mock_get_client):
        """Test that default behavior (no parameters) works as before."""
        # Mock Prefect client
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock deployment objects
        mock_deployment1 = Mock()
        mock_deployment1.name = "project1--main--flow1--dev"
        mock_deployment1.tags = ["COMMIT_HASH=abc123", "PACKAGE_VERSION=1.0.0"]
        mock_deployment1.id = "deploy1_id"
        mock_deployment1.created = "2023-01-01"
        mock_deployment1.updated = "2023-01-01"
        mock_deployment1.flow_id = "flow1_id"
        
        mock_deployment2 = Mock()
        mock_deployment2.name = "project1--main--flow2--dev"
        mock_deployment2.tags = ["COMMIT_HASH=def456", "PACKAGE_VERSION=1.0.0"]
        mock_deployment2.id = "deploy2_id"
        mock_deployment2.created = "2023-01-01"
        mock_deployment2.updated = "2023-01-01"
        mock_deployment2.flow_id = "flow2_id"
        
        mock_client.read_deployments.return_value = [mock_deployment1, mock_deployment2]
        
        finder = PrefectDeploymentFinder()
        finder.credentials_verified = True  # Skip credentials check
        
        with patch.dict('os.environ', {'PREFECT_API_URL': 'https://api.prefect.cloud/api/accounts/test/workspaces/test'}):
            result = finder.get_deployments()
            
        assert len(result) == 2
        deploy_names = {d.name for d in result}
        assert "project1--main--flow1--dev" in deploy_names
        assert "project1--main--flow2--dev" in deploy_names

    @pytest.mark.skipif(not PREFECT_AVAILABLE, reason="Prefect not available")
    @patch('acme_portal_sdk.prefect.deployment_finder.get_client')
    def test_prefect_deployment_finder_deployments_to_fetch(self, mock_get_client):
        """Test selective re-fetching by deployments_to_fetch parameter."""
        # Mock Prefect client  
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        mock_deployment1 = Mock()
        mock_deployment1.name = "project1--main--flow1--dev"
        mock_deployment1.tags = ["COMMIT_HASH=abc123", "PACKAGE_VERSION=1.0.0"]
        mock_deployment1.id = "deploy1_id"
        mock_deployment1.created = "2023-01-01"
        mock_deployment1.updated = "2023-01-01"
        mock_deployment1.flow_id = "flow1_id"
        
        mock_deployment2 = Mock()
        mock_deployment2.name = "project1--main--flow2--dev" 
        mock_deployment2.tags = ["COMMIT_HASH=def456", "PACKAGE_VERSION=1.0.0"]
        mock_deployment2.id = "deploy2_id"
        mock_deployment2.created = "2023-01-01"
        mock_deployment2.updated = "2023-01-01"
        mock_deployment2.flow_id = "flow2_id"
        
        mock_client.read_deployments.return_value = [mock_deployment1, mock_deployment2]
        
        finder = PrefectDeploymentFinder()
        finder.credentials_verified = True
        
        with patch.dict('os.environ', {'PREFECT_API_URL': 'https://api.prefect.cloud/api/accounts/test/workspaces/test'}):
            # Only fetch prefect_deployment1
            result = finder.get_deployments(deployments_to_fetch=[self.prefect_deployment1])
            
        assert len(result) == 1
        assert result[0].id == "deploy1_id"

    @pytest.mark.skipif(not PREFECT_AVAILABLE, reason="Prefect not available")
    @patch('acme_portal_sdk.prefect.deployment_finder.get_client')  
    def test_prefect_deployment_finder_flows_to_fetch(self, mock_get_client):
        """Test selective re-fetching by flows_to_fetch parameter."""
        # Mock Prefect client
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        mock_deployment1 = Mock()
        mock_deployment1.name = "project1--main--flow1--dev"
        mock_deployment1.tags = ["COMMIT_HASH=abc123", "PACKAGE_VERSION=1.0.0"]
        mock_deployment1.id = "deploy1_id"
        mock_deployment1.created = "2023-01-01"
        mock_deployment1.updated = "2023-01-01"
        mock_deployment1.flow_id = "flow1_id"
        
        mock_deployment2 = Mock()
        mock_deployment2.name = "project1--main--flow2--dev"
        mock_deployment2.tags = ["COMMIT_HASH=def456", "PACKAGE_VERSION=1.0.0"]
        mock_deployment2.id = "deploy2_id"
        mock_deployment2.created = "2023-01-01"
        mock_deployment2.updated = "2023-01-01"
        mock_deployment2.flow_id = "flow2_id"
        
        mock_client.read_deployments.return_value = [mock_deployment1, mock_deployment2]
        
        finder = PrefectDeploymentFinder()
        finder.credentials_verified = True
        
        with patch.dict('os.environ', {'PREFECT_API_URL': 'https://api.prefect.cloud/api/accounts/test/workspaces/test'}):
            # Only fetch deployments for flow1
            result = finder.get_deployments(flows_to_fetch=[self.flow1])
            
        assert len(result) == 1
        assert result[0].flow_name == "flow1"

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available") 
    @patch('acme_portal_sdk.airflow.deployment_finder.requests')
    def test_airflow_deployment_finder_deployments_to_fetch(self, mock_requests):
        """Test that AirflowDeploymentFinder also supports selective re-fetching."""
        # Mock requests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dags": [
                {
                    "dag_id": "project1--main--flow1--dev",
                    "tags": ["COMMIT_HASH=abc123", "PACKAGE_VERSION=1.0.0"],
                    "is_active": True,
                    "is_paused": False,
                    "created_at": "2023-01-01",
                    "last_parsed_time": "2023-01-01"
                },
                {
                    "dag_id": "project1--main--flow2--dev", 
                    "tags": ["COMMIT_HASH=def456", "PACKAGE_VERSION=1.0.0"],
                    "is_active": True,
                    "is_paused": False,
                    "created_at": "2023-01-01", 
                    "last_parsed_time": "2023-01-01"
                }
            ]
        }
        mock_requests.request.return_value = mock_response
        
        finder = AirflowDeploymentFinder("http://airflow.example.com", "user", "pass")
        finder.credentials_verified = True
        
        # Only fetch airflow_deployment1 
        result = finder.get_deployments(deployments_to_fetch=[self.airflow_deployment1])
        
        assert len(result) == 1
        assert result[0].id == "project1--main--flow1--dev"

    def test_empty_parameters(self, tmp_path):
        """Test that empty lists work correctly."""
        finder = PrefectFlowFinder(str(tmp_path))
        
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2
        }
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            # Empty lists should return no results 
            result = finder.find_flows(flows_to_fetch=[], flow_groups=[])
            
        assert len(result) == 0

    def test_non_matching_parameters(self, tmp_path):
        """Test that non-matching parameters return empty results."""
        finder = PrefectFlowFinder(str(tmp_path))
        
        mock_flows = {
            "flow1_id": self.flow1,
            "flow2_id": self.flow2
        }
        
        non_matching_flow = FlowDetails(
            name="non_matching",
            original_name="non-matching",
            description="Non-matching flow", 
            id="non_matching_id",
            source_path="/path/to/non_matching.py",
            source_relative="non_matching.py"
        )
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            # Non-matching flow should return no results
            result = finder.find_flows(flows_to_fetch=[non_matching_flow])
            
        assert len(result) == 0
        
        with patch.object(finder, '_scan_directory', return_value=mock_flows):
            # Non-matching group should return no results  
            result = finder.find_flows(flow_groups=["non_matching_group"])
            
        assert len(result) == 0