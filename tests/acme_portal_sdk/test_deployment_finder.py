import pytest
from acme_portal_sdk.deployment_finder import DeploymentDetails


class TestDeploymentDetails:
    """Test DeploymentDetails functionality including child_attributes support."""

    def test_deployment_details_basic_creation(self):
        """Test basic DeploymentDetails creation without child_attributes."""
        deployment = DeploymentDetails(
            name="test_deployment",
            project_name="test_project",
            branch="main",
            flow_name="test_flow",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1", "tag2"],
            id="deploy_id",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            flow_id="flow_id",
            url="https://example.com/deployment",
        )
        
        assert deployment.name == "test_deployment"
        assert deployment.child_attributes == {}

    def test_deployment_details_with_child_attributes(self):
        """Test DeploymentDetails creation with child_attributes."""
        child_attrs = {"region": "us-east-1", "cpu_limit": "2000m"}
        
        deployment = DeploymentDetails(
            name="test_deployment",
            project_name="test_project",
            branch="main",
            flow_name="test_flow",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1", "tag2"],
            id="deploy_id",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            flow_id="flow_id",
            url="https://example.com/deployment",
            child_attributes=child_attrs,
        )
        
        assert deployment.child_attributes == child_attrs

    def test_to_dict_merges_child_attributes(self):
        """Test that to_dict() merges child_attributes into the main dictionary."""
        child_attrs = {"region": "us-east-1", "cpu_limit": "2000m"}
        
        deployment = DeploymentDetails(
            name="test_deployment",
            project_name="test_project",
            branch="main",
            flow_name="test_flow",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1", "tag2"],
            id="deploy_id",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            flow_id="flow_id",
            url="https://example.com/deployment",
            child_attributes=child_attrs,
        )
        
        result = deployment.to_dict()
        
        # Child attributes should be merged into the main dictionary
        assert result["region"] == "us-east-1"
        assert result["cpu_limit"] == "2000m"
        assert result["name"] == "test_deployment"
        
        # child_attributes key should not be present in the result
        assert "child_attributes" not in result

    def test_to_dict_without_child_attributes(self):
        """Test that to_dict() works correctly when child_attributes is empty."""
        deployment = DeploymentDetails(
            name="test_deployment",
            project_name="test_project",
            branch="main",
            flow_name="test_flow",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1", "tag2"],
            id="deploy_id",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            flow_id="flow_id",
            url="https://example.com/deployment",
        )
        
        result = deployment.to_dict()
        
        # Should contain all standard fields
        assert result["name"] == "test_deployment"
        assert result["env"] == "dev"
        
        # child_attributes key should not be present
        assert "child_attributes" not in result

    def test_from_dict_extracts_child_attributes(self):
        """Test that from_dict() properly extracts child_attributes."""
        data = {
            "name": "test_deployment",
            "project_name": "test_project",
            "branch": "main",
            "flow_name": "test_flow",
            "env": "dev",
            "commit_hash": "abc123",
            "package_version": "1.0.0",
            "tags": ["tag1", "tag2"],
            "id": "deploy_id",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "flow_id": "flow_id",
            "url": "https://example.com/deployment",
            # These should become child_attributes
            "region": "us-east-1",
            "cpu_limit": "2000m",
        }
        
        deployment = DeploymentDetails.from_dict(data)
        
        assert deployment.name == "test_deployment"
        assert deployment.child_attributes["region"] == "us-east-1"
        assert deployment.child_attributes["cpu_limit"] == "2000m"

    def test_from_dict_with_explicit_child_attributes(self):
        """Test from_dict() when child_attributes is explicitly provided."""
        data = {
            "name": "test_deployment",
            "project_name": "test_project",
            "branch": "main",
            "flow_name": "test_flow",
            "env": "dev",
            "commit_hash": "abc123",
            "package_version": "1.0.0",
            "tags": ["tag1", "tag2"],
            "id": "deploy_id",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "flow_id": "flow_id",
            "url": "https://example.com/deployment",
            "child_attributes": {"existing_attr": "existing_value"},
            # This should also be added to child_attributes
            "region": "us-east-1",
        }
        
        deployment = DeploymentDetails.from_dict(data)
        
        assert deployment.name == "test_deployment"
        assert deployment.child_attributes["existing_attr"] == "existing_value"
        assert deployment.child_attributes["region"] == "us-east-1"

    def test_round_trip_serialization(self):
        """Test that to_dict() and from_dict() work together properly."""
        original_deployment = DeploymentDetails(
            name="test_deployment",
            project_name="test_project",
            branch="main",
            flow_name="test_flow",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1", "tag2"],
            id="deploy_id",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            flow_id="flow_id",
            url="https://example.com/deployment",
            child_attributes={"region": "us-east-1", "cpu_limit": "2000m"},
        )
        
        # Convert to dict and back
        data = original_deployment.to_dict()
        reconstructed_deployment = DeploymentDetails.from_dict(data)
        
        # Should be equivalent
        assert reconstructed_deployment.name == original_deployment.name
        assert reconstructed_deployment.child_attributes == original_deployment.child_attributes

    def test_subclass_usage(self):
        """Test that subclasses can properly use child_attributes."""
        from dataclasses import dataclass
        
        @dataclass
        class ExtendedDeploymentDetails(DeploymentDetails):
            def __init__(self, region: str = "us-east-1", cpu_limit: str = "1000m", **kwargs):
                # Custom initialization logic
                child_attributes = kwargs.pop('child_attributes', {})
                child_attributes.update({
                    "region": region,
                    "cpu_limit": cpu_limit
                })
                super().__init__(child_attributes=child_attributes, **kwargs)
        
        extended_deployment = ExtendedDeploymentDetails(
            name="test_deployment",
            project_name="test_project",
            branch="main",
            flow_name="test_flow",
            env="dev",
            commit_hash="abc123",
            package_version="1.0.0",
            tags=["tag1", "tag2"],
            id="deploy_id",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            flow_id="flow_id",
            url="https://example.com/deployment",
            region="us-west-2",
            cpu_limit="4000m",
        )
        
        assert extended_deployment.child_attributes["region"] == "us-west-2"
        assert extended_deployment.child_attributes["cpu_limit"] == "4000m"
        
        # Test serialization works
        data = extended_deployment.to_dict()
        assert data["region"] == "us-west-2"
        assert data["cpu_limit"] == "4000m"
        assert "child_attributes" not in data