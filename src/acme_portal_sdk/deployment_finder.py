from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class DeploymentDetails:
    """Holds details about an existing deployment.

    Attributes:
        name: Original name of the deployment config in the deployment system
        project_name: Project name to which the deployment belongs to (repo name)
        branch: Branch of code which is run in the deployment
        flow_name: Name of the flow run in the deployment
        env: Environment/Namespace for which the deployment is run (e.g., dev, prod)
        commit_hash: Commit hash of the code in the deployment
        package_version: Package version of the code in the deployment
        tags: Tags associated with the deployment
        id: Unique identifier for the deployment in the end system
        created_at: Timestamp of when the deployment was created
        updated_at: Timestamp of when the deployment was last updated
        flow_id: Unique identifier for the flow in the deployment system
        url: URL to the deployment in the deployment system
        child_attributes: Additional attributes that can be set by subclasses
    """

    name: str
    project_name: str
    branch: str
    flow_name: str
    env: str
    commit_hash: str
    package_version: str
    tags: List[str]
    id: str
    created_at: str
    updated_at: str
    flow_id: str
    url: str
    child_attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the DeploymentDetails to a dictionary suitable for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeploymentDetails":
        """Create a DeploymentDetails instance from a dictionary representation."""
        return cls(**data)


class DeploymentFinder(ABC):
    """Discovers existing deployments in target environments, with implementations providing environment-specific discovery."""

    @abstractmethod
    def get_deployments(self) -> List[DeploymentDetails]:
        """Method to find deployments, to be implemented by subclasses."""
        pass

    def __call__(self) -> List[Dict[str, Any]]:
        return [x.to_dict() for x in self.get_deployments()]
