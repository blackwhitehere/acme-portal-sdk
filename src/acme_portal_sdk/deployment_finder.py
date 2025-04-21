from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class DeploymentDetails:
    """Holds details about an existing deployment."""

    name: str  # Original name of the deployment config in the deployment system
    project_name: str  # Project name to which the deployment belongs to (repo name)
    branch: str  # Branch of code which is run in the deployment
    flow_name: str  # Name of the flow run in the deployment
    env: str  # Environment/Namespace for which the deployment is run (e.g., dev, prod)
    commit_hash: str  # Commit hash of the code in the deployment
    package_version: str  # Package version of the code in the deployment
    tags: List[str]  # Tags associated with the deployment
    id: str  # Unique identifier for the deployment in the end system
    created_at: str  # Timestamp of when the deployment was created
    updated_at: str  # Timestamp of when the deployment was last updated
    flow_id: str  # Unique identifier for the flow in the deployment system


class DeploymentFinder(ABC):
    """Discovers existing deployments in target environments, with implementations providing environment-specific discovery."""

    @abstractmethod
    def get_deployments(self) -> List[DeploymentDetails]:
        """Method to find deployments, to be implemented by subclasses."""
        pass

    def __call__(self) -> List[DeploymentDetails]:
        return self.get_deployments()
