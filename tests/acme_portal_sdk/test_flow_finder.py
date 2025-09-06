from acme_portal_sdk.flow_finder import FlowDetails


class TestFlowDetails:
    """Test FlowDetails functionality including child_attributes support."""

    def test_flow_details_basic_creation(self):
        """Test basic FlowDetails creation without child_attributes."""
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            id="test_id",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            grouping=["group1", "group2"],
        )
        
        assert flow.name == "test_flow"
        assert flow.child_attributes == {}

    def test_flow_details_with_child_attributes(self):
        """Test FlowDetails creation with child_attributes."""
        child_attrs = {
            "custom_field": "custom_value", 
            "priority": 1,
            # Prefect-specific attributes that would be set by PrefectFlowFinder
            "obj_name": "test_func",  # Needed for deployment
            "module": "test_module",
            "import_path": "test_module.source"
        }
        
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            id="test_id",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            grouping=["group1", "group2"],
            child_attributes=child_attrs,
        )
        
        assert flow.child_attributes == child_attrs

    def test_to_dict_keeps_child_attributes_separate(self):
        """Test that to_dict() keeps child_attributes as a separate key."""
        child_attrs = {
            "custom_field": "custom_value", 
            "priority": 1,
            "obj_name": "test_func",  # needed for deployment
            "module": "test_module"
        }
        
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            id="test_id",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            grouping=["group1", "group2"],
            child_attributes=child_attrs,
        )
        
        result = flow.to_dict()
        
        # Child attributes should be kept as a separate key
        assert "child_attributes" in result
        assert result["child_attributes"] == child_attrs
        assert result["name"] == "test_flow"
        
        # Custom attributes should not be merged into the main dictionary
        assert "custom_field" not in result
        assert "priority" not in result
        assert "obj_name" not in result  # Should be in child_attributes only
        assert "module" not in result   # Should be in child_attributes only

    def test_to_dict_with_empty_child_attributes(self):
        """Test that to_dict() includes child_attributes even when empty."""
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            id="test_id",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            grouping=["group1", "group2"],
        )
        
        result = flow.to_dict()
        
        # Should contain all standard fields
        assert result["name"] == "test_flow"
        assert result["description"] == "Test flow description"
        
        # child_attributes key should be present even if empty
        assert "child_attributes" in result
        assert result["child_attributes"] == {}

    def test_from_dict_with_child_attributes(self):
        """Test that from_dict() properly handles child_attributes."""
        data = {
            "name": "test_flow",
            "original_name": "test-flow",
            "description": "Test flow description",
            "id": "test_id",
            "source_path": "/path/to/source.py",
            "source_relative": "relative/path.py",
            "grouping": ["group1", "group2"],
            "child_attributes": {
                "custom_field": "custom_value",
                "priority": 1,
                "obj_name": "test_func",  # needed for deployment
                "module": "test_module",
            }
        }
        
        flow = FlowDetails.from_dict(data)
        
        assert flow.name == "test_flow"
        assert flow.child_attributes["custom_field"] == "custom_value"
        assert flow.child_attributes["priority"] == 1
        assert flow.child_attributes["obj_name"] == "test_func"  # needed for deployment

    def test_from_dict_without_child_attributes(self):
        """Test from_dict() when child_attributes is not provided."""
        data = {
            "name": "test_flow",
            "original_name": "test-flow",
            "description": "Test flow description",
            "id": "test_id",
            "source_path": "/path/to/source.py",
            "source_relative": "relative/path.py",
            "grouping": ["group1", "group2"],
        }
        
        flow = FlowDetails.from_dict(data)
        
        assert flow.name == "test_flow"
        assert flow.child_attributes == {}

    def test_round_trip_serialization(self):
        """Test that to_dict() and from_dict() work together properly."""
        original_flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            id="test_id",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            grouping=["group1", "group2"],
            child_attributes={
                "custom_field": "custom_value", 
                "priority": 1,
                "obj_type": "function",
                "obj_name": "test_func",
                "module": "test_module",
            },
        )
        
        # Convert to dict and back
        data = original_flow.to_dict()
        reconstructed_flow = FlowDetails.from_dict(data)
        
        # Should be equivalent
        assert reconstructed_flow.name == original_flow.name
        assert reconstructed_flow.child_attributes == original_flow.child_attributes

    def test_subclass_usage(self):
        """Test that subclasses can properly use child_attributes."""
        from dataclasses import dataclass
        
        @dataclass
        class ExtendedFlowDetails(FlowDetails):
            def __init__(self, priority: int = 0, category: str = "default", **kwargs):
                # Custom initialization logic
                child_attributes = kwargs.pop('child_attributes', {})
                child_attributes.update({
                    "priority": priority,
                    "category": category
                })
                super().__init__(child_attributes=child_attributes, **kwargs)
        
        extended_flow = ExtendedFlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            id="test_id",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            grouping=["group1", "group2"],
            priority=5,
            category="important",
        )
        
        assert extended_flow.child_attributes["priority"] == 5
        assert extended_flow.child_attributes["category"] == "important"
        
        # Test serialization keeps child_attributes separate
        data = extended_flow.to_dict()
        assert "child_attributes" in data
        assert data["child_attributes"]["priority"] == 5
        assert data["child_attributes"]["category"] == "important"
        # Custom attributes should not be in the main dictionary
        assert "priority" not in data
        assert "category" not in data
