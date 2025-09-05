# API Migration Guide

## FlowDetails API Changes in v1.0.0

Version 1.0.0 moves implementation-specific attributes to `child_attributes`.

### Changes

**Before:**
```python
FlowDetails(
    name="my_flow",
    obj_type="function",
    obj_name="my_function",
    obj_parent_type="module",
    obj_parent="my_module",
    module="my_module",
    import_path="my.module",
)
```

**After:**
```python
FlowDetails(
    name="my_flow",
    id="flow_123",
    source_path="/path/to/file.py",
    source_relative="file.py",
    child_attributes={
        "obj_type": "function",
        "obj_name": "my_function",
        "obj_parent_type": "module",
        "obj_parent": "my_module",
        "module": "my_module",
        "import_path": "my.module",
    }
)
```

### Moved Attributes

These attributes moved to `child_attributes`:
- `obj_type`, `obj_name`, `obj_parent_type`, `obj_parent`, `module`, `import_path`

Access via: `flow.child_attributes["attribute_name"]`

### Migration by User Type

#### Platform Users (Prefect/Airflow)

No setup changes required. Update attribute access:

**Before:**
```python
obj_type = flows[0].obj_type
obj_name = flows[0].obj_name
```

**After:**
```python
obj_type = flows[0].child_attributes["obj_type"]
obj_name = flows[0].child_attributes["obj_name"]
```

#### Custom Implementation Developers

Update your `FlowDetails` creation to use `child_attributes` for implementation-specific data.

**Before v1.0.0:**
```python
from acme_portal_sdk.flow_details import FlowDetails

flow = FlowDetails(
    name="my_flow",
    original_name="my_flow",
    description="My custom flow",
    id="flow_001",
    source_path="/src/flows/my_flow.py",
    source_relative="flows/my_flow.py",
    obj_type="function",
    obj_name="run_flow", 
    obj_parent_type="module",
    obj_parent="flows.my_flow",
    module="flows.my_flow",
    import_path="flows.my_flow"
)
```

**After v1.0.0:**
```python
from acme_portal_sdk.flow_details import FlowDetails

flow = FlowDetails(
    name="my_flow",
    original_name="my_flow", 
    description="My custom flow",
    id="flow_001",
    source_path="/src/flows/my_flow.py",
    source_relative="flows/my_flow.py",
    child_attributes={
        "obj_type": "function",
        "obj_name": "run_flow",
        "obj_parent_type": "module", 
        "obj_parent": "flows.my_flow",
        "module": "flows.my_flow",
        "import_path": "flows.my_flow",
        # Add any custom metadata here
        "priority": "high",
        "team": "data-engineering"
    }
)
```

#### SDK Extenders

You can now store custom metadata in `child_attributes` without conflicts, eliminating the need to subclass `FlowDetails` for most customization needs.

**Before v1.0.0:**
```python
# Had to subclass to add custom attributes
class CustomFlowDetails(FlowDetails):
    def __init__(self, priority=None, team=None, **kwargs):
        super().__init__(**kwargs)
        self.priority = priority
        self.team = team
```

**After v1.0.0:**
```python
# Use child_attributes for custom metadata
flow = FlowDetails(
    name="my_flow",
    # ... required attributes ...
    child_attributes={
        # Standard implementation attributes
        "obj_type": "function",
        "module": "my_module",
        # Custom attributes
        "priority": "high",
        "team": "data-engineering",
        "cost_center": "analytics",
        "compliance_level": "strict"
    }
)
```

### Deployment Integration Changes

If you're using flow deployment functionality, update attribute access:

**Before v1.0.0:**
```python
# Deploy flows using direct attribute access
deploy_flow(
    flow_name=flow.name,
    module=flow.module,
    import_path=flow.import_path
)
```

**After v1.0.0:**  
```python
# Deploy flows using child_attributes access
deploy_flow(
    flow_name=flow.name,
    module=flow.child_attributes["module"],
    import_path=flow.child_attributes["import_path"]
)
```

### Validation and Error Handling

The new architecture includes better validation and clearer error messages:

```python
# If a required child_attribute is missing, you'll get a clear error
try:
    module = flow.child_attributes["module"]
except KeyError:
    print("This flow doesn't have module information in child_attributes")
    
# Check if attribute exists before accessing
if "priority" in flow.child_attributes:
    priority = flow.child_attributes["priority"]
else:
    priority = "normal"  # default value
```

### Backward Compatibility Notes

- **Binary compatibility**: There is no backward compatibility at the binary level - this is a breaking change
- **Runtime compatibility**: Existing `PrefectFlowFinder` and `AirflowFlowFinder` usage continues to work
- **API compatibility**: Direct attribute access (`flow.obj_type`) will raise `AttributeError` - must use `flow.child_attributes["obj_type"]`

### Testing Your Migration

To verify your migration is successful:

1. **Run your existing flow discovery code** - it should work without modification
2. **Update attribute access patterns** - replace direct access with `child_attributes` dictionary access  
3. **Test deployment workflows** - ensure they use the new attribute access pattern
4. **Validate custom metadata** - confirm your custom attributes are properly stored in `child_attributes`

### Getting Help

If you encounter issues during migration:

1. Check that you're accessing implementation-specific attributes via `child_attributes`
2. Verify that your custom `FlowDetails` creation uses the new constructor signature
3. Review this migration guide for examples matching your use case
4. Open an issue on GitHub with your specific migration challenge

This migration enables a more flexible and maintainable architecture while preserving the ease of use for platform-specific implementations.