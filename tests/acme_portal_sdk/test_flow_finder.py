import pytest
from acme_portal_sdk.flow_finder import FlowDetails


class TestFlowDetails:
    """Test FlowDetails functionality including child_attributes support."""

    def test_flow_details_basic_creation(self):
        """Test basic FlowDetails creation without child_attributes."""
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            obj_type="function",
            obj_name="test_func",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
        )
        
        assert flow.name == "test_flow"
        assert flow.child_attributes == {}

    def test_flow_details_with_child_attributes(self):
        """Test FlowDetails creation with child_attributes."""
        child_attrs = {"custom_field": "custom_value", "priority": 1}
        
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            obj_type="function",
            obj_name="test_func",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
            child_attributes=child_attrs,
        )
        
        assert flow.child_attributes == child_attrs

    def test_to_dict_merges_child_attributes(self):
        """Test that to_dict() merges child_attributes into the main dictionary."""
        child_attrs = {"custom_field": "custom_value", "priority": 1}
        
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            obj_type="function",
            obj_name="test_func",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
            child_attributes=child_attrs,
        )
        
        result = flow.to_dict()
        
        # Child attributes should be merged into the main dictionary
        assert result["custom_field"] == "custom_value"
        assert result["priority"] == 1
        assert result["name"] == "test_flow"
        
        # child_attributes key should not be present in the result
        assert "child_attributes" not in result

    def test_to_dict_without_child_attributes(self):
        """Test that to_dict() works correctly when child_attributes is empty."""
        flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            obj_type="function",
            obj_name="test_func",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
        )
        
        result = flow.to_dict()
        
        # Should contain all standard fields
        assert result["name"] == "test_flow"
        assert result["obj_type"] == "function"
        
        # child_attributes key should not be present
        assert "child_attributes" not in result

    def test_from_dict_extracts_child_attributes(self):
        """Test that from_dict() properly extracts child_attributes."""
        data = {
            "name": "test_flow",
            "original_name": "test-flow",
            "description": "Test flow description",
            "obj_type": "function",
            "obj_name": "test_func",
            "obj_parent_type": "module",
            "obj_parent": "test_module",
            "id": "test_id",
            "module": "test_module",
            "source_path": "/path/to/source.py",
            "source_relative": "relative/path.py",
            "import_path": "test_module.source",
            "grouping": ["group1", "group2"],
            # These should become child_attributes
            "custom_field": "custom_value",
            "priority": 1,
        }
        
        flow = FlowDetails.from_dict(data)
        
        assert flow.name == "test_flow"
        assert flow.child_attributes["custom_field"] == "custom_value"
        assert flow.child_attributes["priority"] == 1

    def test_from_dict_with_explicit_child_attributes(self):
        """Test from_dict() when child_attributes is explicitly provided."""
        data = {
            "name": "test_flow",
            "original_name": "test-flow",
            "description": "Test flow description",
            "obj_type": "function",
            "obj_name": "test_func",
            "obj_parent_type": "module",
            "obj_parent": "test_module",
            "id": "test_id",
            "module": "test_module",
            "source_path": "/path/to/source.py",
            "source_relative": "relative/path.py",
            "import_path": "test_module.source",
            "grouping": ["group1", "group2"],
            "child_attributes": {"existing_attr": "existing_value"},
            # This should also be added to child_attributes
            "custom_field": "custom_value",
        }
        
        flow = FlowDetails.from_dict(data)
        
        assert flow.name == "test_flow"
        assert flow.child_attributes["existing_attr"] == "existing_value"
        assert flow.child_attributes["custom_field"] == "custom_value"

    def test_round_trip_serialization(self):
        """Test that to_dict() and from_dict() work together properly."""
        original_flow = FlowDetails(
            name="test_flow",
            original_name="test-flow",
            description="Test flow description",
            obj_type="function",
            obj_name="test_func",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
            child_attributes={"custom_field": "custom_value", "priority": 1},
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
            obj_type="function",
            obj_name="test_func",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
            priority=5,
            category="important",
        )
        
        assert extended_flow.child_attributes["priority"] == 5
        assert extended_flow.child_attributes["category"] == "important"
        
        # Test serialization works
        data = extended_flow.to_dict()
        assert data["priority"] == 5
        assert data["category"] == "important"
        assert "child_attributes" not in data