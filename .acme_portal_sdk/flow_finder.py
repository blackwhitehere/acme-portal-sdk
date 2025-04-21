from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder, PrefectFlowDetails  # noqa: F401
from pathlib import Path

# Create an instance of PrefectFlowFinder
project_root = Path(__file__).parent.parent
flow_finder = PrefectFlowFinder(root_dir=str(project_root / "examples" / "flows"))

if __name__ == "__main__":
    from pprint import pprint

    pprint(flow_finder.find_flows())
