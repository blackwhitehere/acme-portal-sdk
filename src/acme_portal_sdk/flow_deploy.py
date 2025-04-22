from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class DeployInfo:
    """Holds configuration required to deploy a flow.

    Flow deployment contains configuration that defines how to run a unit of work (flow).
    """

    name: str  # Name of the deployment
    flow_name: str  # Normalized name of the flow to deploy (from FlowDetails.name)
    work_pool_name: Optional[str] = (
        None  # Name of the work pool to use for the deployment, controls which group of resources is used to execute the flow run
    )
    work_queue_name: Optional[str] = (
        None  # Name of the work queue to use for the deployment, controls priority of using resources in the pool
    )
    parameters: Optional[dict[str, Any]] = (
        None  # Parameters to pass to the flow when it runs
    )
    job_variables: Optional[dict] = None  # Variables to pass to the job when it runs
    cron: Optional[str] = None  # Cron schedule for the deployment
    paused: Optional[bool] = False  # Whether the deployment is in an inactive state
    concurrency_limit: Optional[int] = (
        1  # Controls possible number of concurrent flow runs
    )
    description: Optional[str] = (
        None  # Description of the deployment, overriding the flow description
    )
    tags: Optional[list[str]] = (
        None  # Tags to associate with the deployment, for categorization and filtering
    )


class DeployInfoPrep(ABC):
    """
    Responsible for preparing and validating deployment information before
    a flow is deployed to a target environment.
    """

    @abstractmethod
    def prep_deploy_info(self, *args, **kwargs) -> List[DeployInfo]:
        """
        Prepare all deployment information needed to deploy.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            DeployInfo object with the prepared deployment information
        """
        pass


class FlowDeployer(ABC):
    """Deploys flows, with implementations handling the deployment to specific execution environment."""

    @abstractmethod
    def deploy(self, flow_deploy_info: DeployInfo) -> None:
        """
        Deploy a flow.

        Args:
            flow_deploy_info: Configuration for the deployment
        """
        pass


class DeployWorkflow(ABC):
    """Encapsulates the deployment workflow for a flow."""

    @abstractmethod
    def run(self, flows_to_deploy: List[str], ref: str) -> Optional[str]:
        """
        Run the deployment workflow for the specified flows.

        Args:
            flows_to_deploy: List of flow names to deploy
            ref: The git ref (branch/tag) for the workflow
        Returns:
            Optional[str]: URL of the deployment if successful, None otherwise
        """
        pass

    def __call__(self, *args, **kwargs) -> Optional[str]:
        """
        Call the run method with the provided arguments.

        Args:
            **args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Optional[str]: URL of the deployment if successful, None otherwise
        """
        return self.run(*args, **kwargs)
