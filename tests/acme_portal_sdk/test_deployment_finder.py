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

    def test_to_dict_keeps_child_attributes_separate(self):
        """Test that to_dict() keeps child_attributes as a separate key."""
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
        
        # Child attributes should be kept as a separate key
        assert "child_attributes" in result
        assert result["child_attributes"] == child_attrs
        assert result["name"] == "test_deployment"
        
        # Custom attributes should not be merged into the main dictionary
        assert "region" not in result
        assert "cpu_limit" not in result

    def test_to_dict_with_empty_child_attributes(self):
        """Test that to_dict() includes child_attributes even when empty."""
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
        
        # child_attributes key should be present even if empty
        assert "child_attributes" in result
        assert result["child_attributes"] == {}

    def test_from_dict_with_child_attributes(self):
        """Test that from_dict() properly handles child_attributes."""
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
            "child_attributes": {
                "region": "us-east-1",
                "cpu_limit": "2000m",
            }
        }
        
        deployment = DeploymentDetails.from_dict(data)
        
        assert deployment.name == "test_deployment"
        assert deployment.child_attributes["region"] == "us-east-1"
        assert deployment.child_attributes["cpu_limit"] == "2000m"

    def test_from_dict_without_child_attributes(self):
        """Test from_dict() when child_attributes is not provided."""
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
        }
        
        deployment = DeploymentDetails.from_dict(data)
        
        assert deployment.name == "test_deployment"
        assert deployment.child_attributes == {}

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
        
        # Test serialization keeps child_attributes separate
        data = extended_deployment.to_dict()
        assert "child_attributes" in data
        assert data["child_attributes"]["region"] == "us-west-2"
        assert data["child_attributes"]["cpu_limit"] == "4000m"
        # Custom attributes should not be in the main dictionary
        assert "region" not in data
        assert "cpu_limit" not in data