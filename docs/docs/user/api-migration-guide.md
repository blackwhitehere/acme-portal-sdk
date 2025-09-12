# API Migration Guide

Breaking changes and migration steps for major API updates.

## v1.2.0

### PrefectFlowAttributes Simplification

Removed three attributes that were not useful for core functionality:

**Removed attributes:**
- `obj_type` - Type of object defining the flow ("function" or "method")
- `obj_parent_type` - Type of container for the flow object ("module" or "class") 
- `obj_parent` - Name of the module or class containing the flow

**Retained attributes:**
- `obj_name` - Name of the function/method (required for deployment functionality)
- `module` - Python module name where the flow is defined
- `import_path` - Full Python import path to the source file

#### Migration Guide

**Before:**
```python
# PrefectFlowAttributes with 6 attributes
attrs = PrefectFlowAttributes(
    obj_type="function",
    obj_name="my_function", 
    obj_parent_type="module",
    obj_parent="my_module",
    module="my_module",
    import_path="my_module.file"
)
```

**After:**
```python
# PrefectFlowAttributes with 3 attributes
attrs = PrefectFlowAttributes(
    obj_name="my_function",  # Required for deployment
    module="my_module",
    import_path="my_module.file"
)
```

**Accessing attributes via FlowDetails:**
```python
# Before - accessing removed attributes
flow.child_attributes["obj_type"]        # No longer available
flow.child_attributes["obj_parent_type"] # No longer available  
flow.child_attributes["obj_parent"]      # No longer available

# After - accessing remaining attributes
flow.child_attributes["obj_name"]        # Still available (required for deployment)
flow.child_attributes["module"]          # Still available
flow.child_attributes["import_path"]     # Still available
```

## FlowDetails API Changes in v1.0.0

Version 1.0.0 changes the `FlowDetails` class structure for more flexibility. Implementation-specific attributes are now stored in the `child_attributes` dictionary instead of as constructor parameters.

### API Changes

**Before v1.0.0:**
```python
# Old API - implementation details required in base class
FlowDetails(
    name="my_flow",
    obj_type="function",      # Implementation detail
    obj_name="my_function",   # Implementation detail  
    obj_parent_type="module", # Implementation detail
    obj_parent="my_module",   # Implementation detail
    module="my_module",       # Implementation detail
    import_path="my.module",  # Implementation detail
)
```

**After v1.0.0:**
```python
# New API - implementation details in child_attributes
FlowDetails(
    name="my_flow",
    id="flow_123",
    source_path="/path/to/file.py",
    source_relative="file.py",
    child_attributes={
        "obj_type": "function",      # Implementation detail
        "obj_name": "my_function",   # Implementation detail
        "obj_parent_type": "module", # Implementation detail
        "obj_parent": "my_module",   # Implementation detail
        "module": "my_module",       # Implementation detail
        "import_path": "my.module",  # Implementation detail
    }
)
```

### Breaking Changes Summary

The following attributes have been **removed as required parameters** from the `FlowDetails` constructor:

- `obj_type` - Type of object (function, method, class)
- `obj_name` - Name of the implementing object  
- `obj_parent_type` - Type of parent container (module, class)
- `obj_parent` - Name of parent container
- `module` - Python module name
- `import_path` - Full import path

These attributes are now stored in the `child_attributes` dictionary and accessed via `flow.child_attributes["attribute_name"]`.

### Migration Instructions

#### Platform Implementation Users (Prefect/Airflow)

**No changes required** to your setup code. Update attribute access patterns:

**Before v1.0.0:**
```python
from acme_portal_sdk.prefect import PrefectFlowFinder

finder = PrefectFlowFinder("./flows")
flows = finder.find_flows()

# Access implementation-specific attributes directly
obj_type = flows[0].obj_type
obj_name = flows[0].obj_name
module = flows[0].module
```

**After v1.0.0:**
```python
from acme_portal_sdk.prefect import PrefectFlowFinder

finder = PrefectFlowFinder("./flows")  # No change needed
flows = finder.find_flows()            # No change needed

# Access implementation-specific attributes via child_attributes
obj_type = flows[0].child_attributes["obj_type"]
obj_name = flows[0].child_attributes["obj_name"] 
module = flows[0].child_attributes["module"]
```

#### Custom Implementation Developers

Update your `FlowDetails` creation to use `child_attributes`:

**Before v1.0.0:**
```python
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

Use `child_attributes` for custom metadata without conflicts:

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

Update attribute access for flow deployment:

**Before v1.0.0:**
```python
deploy_flow(
    flow_name=flow.name,
    module=flow.module,
    import_path=flow.import_path
)
```

**After v1.0.0:**  
```python
deploy_flow(
    flow_name=flow.name,
    module=flow.child_attributes["module"],
    import_path=flow.child_attributes["import_path"]
)
```

### Validation and Error Handling

```python
# Check if attribute exists before accessing
try:
    module = flow.child_attributes["module"]
except KeyError:
    print("This flow doesn't have module information in child_attributes")
    
# Use get() method with default
priority = flow.child_attributes.get("priority", "normal")
```

### Backward Compatibility Notes

- **Binary compatibility**: No backward compatibility - this is a breaking change
- **Runtime compatibility**: Existing `PrefectFlowFinder` and `AirflowFlowFinder` usage continues to work
- **API compatibility**: Direct attribute access (`flow.obj_type`) will raise `AttributeError` - must use `flow.child_attributes["obj_type"]`

### Testing Your Migration

1. **Run your existing flow discovery code** - it should work without modification
2. **Update attribute access patterns** - replace direct access with `child_attributes` dictionary access  
3. **Test deployment workflows** - ensure they use the new attribute access pattern
4. **Validate custom metadata** - confirm your custom attributes are properly stored in `child_attributes`
