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

    def test_to_dict_keeps_child_attributes_separate(self):
        """Test that to_dict() keeps child_attributes as a separate key."""
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
        
        # Child attributes should be kept as a separate key
        assert "child_attributes" in result
        assert result["child_attributes"] == child_attrs
        assert result["name"] == "test_flow"
        
        # Custom attributes should not be merged into the main dictionary
        assert "custom_field" not in result
        assert "priority" not in result

    def test_to_dict_with_empty_child_attributes(self):
        """Test that to_dict() includes child_attributes even when empty."""
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
        
        # child_attributes key should be present even if empty
        assert "child_attributes" in result
        assert result["child_attributes"] == {}

    def test_from_dict_with_child_attributes(self):
        """Test that from_dict() properly handles child_attributes."""
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
            "child_attributes": {
                "custom_field": "custom_value",
                "priority": 1,
            }
        }
        
        flow = FlowDetails.from_dict(data)
        
        assert flow.name == "test_flow"
        assert flow.child_attributes["custom_field"] == "custom_value"
        assert flow.child_attributes["priority"] == 1

    def test_from_dict_without_child_attributes(self):
        """Test from_dict() when child_attributes is not provided."""
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
        
        # Test serialization keeps child_attributes separate
        data = extended_flow.to_dict()
        assert "child_attributes" in data
        assert data["child_attributes"]["priority"] == 5
        assert data["child_attributes"]["category"] == "important"
        # Custom attributes should not be in the main dictionary
        assert "priority" not in data
        assert "category" not in data

    def test_line_number_field(self):
        """Test that line_number field works correctly."""
        # Test with line number
        flow_with_line = FlowDetails(
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
            line_number=42,
            grouping=["group1", "group2"],
        )
        
        assert flow_with_line.line_number == 42
        
        # Test without line number (should default to None)
        flow_without_line = FlowDetails(
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
        
        assert flow_without_line.line_number is None

    def test_line_number_serialization(self):
        """Test that line_number field is properly serialized and deserialized."""
        # Test with line number
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
            line_number=123,
            grouping=["group1", "group2"],
        )
        
        # Serialize to dict
        data = original_flow.to_dict()
        assert "line_number" in data
        assert data["line_number"] == 123
        
        # Deserialize from dict
        reconstructed_flow = FlowDetails.from_dict(data)
        assert reconstructed_flow.line_number == 123
        
        # Test without line number
        flow_without_line = FlowDetails(
            name="test_flow2",
            original_name="test-flow2",
            description="Test flow description",
            obj_type="function",
            obj_name="test_func2",
            obj_parent_type="module",
            obj_parent="test_module",
            id="test_id2",
            module="test_module",
            source_path="/path/to/source.py",
            source_relative="relative/path.py",
            import_path="test_module.source",
            grouping=["group1", "group2"],
        )
        
        # Serialize to dict
        data_no_line = flow_without_line.to_dict()
        assert "line_number" in data_no_line
        assert data_no_line["line_number"] is None
        
        # Deserialize from dict
        reconstructed_no_line = FlowDetails.from_dict(data_no_line)
        assert reconstructed_no_line.line_number is None

    def test_from_dict_with_line_number(self):
        """Test from_dict() when line_number is provided in data."""
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
            "line_number": 999,
            "grouping": ["group1", "group2"],
        }
        
        flow = FlowDetails.from_dict(data)
        assert flow.line_number == 999

    def test_from_dict_without_line_number(self):
        """Test from_dict() when line_number is not provided in data."""
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
        }
        
        flow = FlowDetails.from_dict(data)
        assert flow.line_number is None