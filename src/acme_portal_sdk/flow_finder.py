from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class FlowDetails:
    """Holds details about a flow.

    Flow (often named Workflow/Job/DAG) is a unit of work in a program.
    """

    name: str  # Display name, may be a normalized version of the original name
    original_name: str  # Name as defined in the code
    description: str  # Description of the flow
    obj_type: str  # Type of object defining the flow (e.g., function, method)
    obj_name: (
        str  # Name of the object defining the flow (e.g., function name, method name)
    )
    obj_parent_type: (
        str  # Type of container for object defining the flow (e.g. class, module)
    )
    obj_parent: str  # Name of container for flow object (e.g., class name if method, module name if function)
    id: str  # Unique identifier for the flow definition in memory
    module: str  # Module name where the flow is defined
    source_path: str  # Unambiguous path to the source file from the root of the project
    source_relative: str  # Relative path to the source file from some known root
    import_path: str  # Python import path to the source file
    grouping: List[
        str
    ]  # Desired grouping of the flow in the context of the project (for navigation)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the FlowDetails to a dictionary suitable for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlowDetails":
        """Create a FlowDetails instance from a dictionary representation."""
        return cls(**data)


class FlowFinder(ABC):
    """Finds flows (units of work/programs) in a given context, with implementations providing specific discovery mechanisms."""

    @abstractmethod
    def find_flows(self) -> List[FlowDetails]:
        """Method to find flows, to be implemented by subclasses."""
        pass

    def __call__(self) -> List[Dict[str, Any]]:
        return [x.to_dict() for x in self.find_flows()]
