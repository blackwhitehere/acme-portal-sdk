import argparse
import asyncio
import importlib
import inspect
import logging
import pkgutil
from importlib.util import find_spec

from acme_config import add_main_arguments, load_saved_parameters
from prefect import Flow
from prefect.client.orchestration import get_client

logger = logging.getLogger(__name__)

# TODO: set from acme-config/local config file
DEFAULT_WORK_POOL = "ecs-pool"
STATIC_CONFIG = {
    "fetch_yahoo_data": {
        "name": "fetch_yahoo_data",
        "import_path": "acme_prefect.flows.fetch_yahoo_data:main",
        "cron": "0 12 * * 1-5",
        "description": "Fetches Yahoo Finance data with minute-level granularity",
        "work_pool_name": "ecs-pool",
    },
    "hello_dw": {
        "name": "hello_dw",
        "import_path": "acme_prefect.flows.hello_dw:main",
        "cron": "0 12 * * 1-5",
        "description": "Hello DW",
        "work_pool_name": "ecs-pool",
    },
    "hello_world": {
        "name": "hello_world",
        "import_path": "acme_prefect.flows.hello_world:hello_world",
        "cron": "0 12 * * 1-5",
        "description": "Hello World",
        "work_pool_name": "ecs-pool",
    },
}


def import_function(module_path, function_name):
    try:
        # Check if module exists
        if find_spec(module_path) is None:
            raise ImportError(f"Module {module_path} not found")

        # Import module
        module = importlib.import_module(module_path)

        # Get function
        if not hasattr(module, function_name):
            raise AttributeError(f"Function {function_name} not found in {module_path}")

        return getattr(module, function_name)

    except Exception as e:
        print(f"Error importing {function_name} from {module_path}: {e}")
        raise


def discover_flows(package_name="acme_prefect.flows"):
    """
    Discovers all Prefect flow functions in the specified package.

    Args:
        package_name: The name of the package to scan for flows

    Returns:
        A dictionary mapping flow names to flow info dictionaries
    """
    flows_dict = {}
    logger.info(f"Discovering flows in package {package_name}")
    try:
        # Import the package
        package = importlib.import_module(package_name)

        # Get the package path
        package_path = package.__path__

        # Iterate through all modules in the package
        for _, module_name, _ in pkgutil.iter_modules(package_path):
            full_module_name = f"{package_name}.{module_name}"

            try:
                module = importlib.import_module(full_module_name)

                # Inspect all module members
                for name, obj in inspect.getmembers(module):
                    if isinstance(obj, Flow):
                        flow_name = obj.name.replace("-", "_")

                        # Extract description from docstring if not explicitly set
                        if hasattr(obj, "description"):
                            description = obj.description
                        elif obj.__doc__:
                            description = inspect.getdoc(obj).strip().split("\n")[0]
                        else:
                            description = f"Flow from {module_name}"

                        flows_dict[flow_name] = {
                            "name": flow_name,
                            "orignal_name": obj.name,
                            "import_path": f"{full_module_name}:{name}",
                            "description": description,
                            "cron": None,
                            "work_pool_name": DEFAULT_WORK_POOL,  # Default work pool
                        }
            except Exception as e:
                logger.warning(f"Error inspecting module {full_module_name}: {e}")

    except Exception as e:
        logger.error(f"Error discovering flows in package {package_name}: {e}")
    logger.info(f"Discovered {len(flows_dict)} flows")
    return flows_dict


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy flows to prefect")
    subparsers = parser.add_subparsers(dest="command")
    # Deploy parser for initial deployment
    deploy_parser = subparsers.add_parser("deploy")
    add_main_arguments(deploy_parser)
    deploy_parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the project",
    )
    deploy_parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the branch",
    )
    deploy_parser.add_argument("-commit-hash", type=str, help="Git commit hash")
    deploy_parser.add_argument("-image-uri", type=str, help="Image URI")
    deploy_parser.add_argument("-package-version", type=str, help="Package version")
    deploy_parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )

    # Promote parser for promoting deployment from one environment to another
    promote_parser = subparsers.add_parser("promote")
    add_main_arguments(promote_parser)
    promote_parser.add_argument("-source-env", type=str, help="Source environment")
    promote_parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the project",
    )
    promote_parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the branch",
    )
    promote_parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )

    return parser.parse_args()


def deploy(args):
    env_vars = load_saved_parameters(args.app_name, args.env, args.ver_number)
    dynamic_config = discover_flows()
    if args.flows_to_deploy == "all":
        flows_to_deploy = dynamic_config.keys()
    else:
        flows_to_deploy = args.flows_to_deploy.split(",")
        flows_to_deploy = [flow_name.replace("-", "_") for flow_name in flows_to_deploy]

    for std_flow_name in flows_to_deploy:
        if std_flow_name in STATIC_CONFIG:
            deploy_config = STATIC_CONFIG[std_flow_name]
        else:
            if std_flow_name not in dynamic_config:
                raise ValueError(f"Flow {std_flow_name} not found in config")
            deploy_config = dynamic_config[std_flow_name]
        module_path, function_name = deploy_config["import_path"].split(":")
        flow_function = import_function(module_path, function_name)
        # align with expectation of flow name being flow function name with underscores
        underscore_flow_name = deploy_config["name"].replace("-", "_")
        if flow_function.name != underscore_flow_name:
            logger.info(
                f"Standardizing flow name {flow_function.name} for deployment to {underscore_flow_name}"
            )
            flow_function.name = underscore_flow_name
        # make sure flow name in deployment name is hyphenated
        hyphen_flow_name = deploy_config["name"].replace("_", "-")
        deployment_name = (
            f"{args.project_name}--{args.branch_name}--{hyphen_flow_name}--{args.env}"
        )
        flow_function.deploy(
            name=deployment_name,
            description=deploy_config["description"],
            # Be careful with work pool setup to avoid issue like this:
            # https://github.com/PrefectHQ/prefect/issues/17249
            work_pool_name=deploy_config["work_pool_name"],
            cron=deploy_config["cron"],
            image=args.image_uri,
            job_variables={
                "env": {**env_vars, "DEPLOYMENT_NAME": deployment_name},
                "image": args.image_uri,
            },
            tags=[
                f"PROJECT_NAME={args.project_name}",
                f"BRANCH_NAME={args.branch_name}",
                f"COMMIT_HASH={args.commit_hash}",
                f"PACKAGE_VERSION={args.package_version}",
            ],
            version=f"{args.branch_name}-{args.commit_hash}",
            build=False,
            push=False,
        )


def extract_tag_value(tags, tag_name):
    return [x for x in tags if x.startswith(f"{tag_name}=")][0].split("=")[1]


def promote(args):
    # todo: use sync_client=True
    client = get_client()
    dynamic_config = discover_flows()
    if args.flows_to_deploy == "all":
        flows_to_deploy = dynamic_config.keys()
    else:
        flows_to_deploy = args.flows_to_deploy.split(",")
        flows_to_deploy = [flow_name.replace("-", "_") for flow_name in flows_to_deploy]

    for std_flow_name in flows_to_deploy:
        if std_flow_name in STATIC_CONFIG:
            deploy_config = STATIC_CONFIG[std_flow_name]
        else:
            if std_flow_name not in dynamic_config:
                raise ValueError(f"Flow {std_flow_name} not found in config")
            deploy_config = dynamic_config[std_flow_name]
        underscore_flow_name = deploy_config["name"].replace("-", "_")
        hyphen_flow_name = deploy_config["name"].replace("_", "-")
        deployment_name = f"{args.project_name}--{args.branch_name}--{hyphen_flow_name}--{args.source_env}"
        try:
            r = dict(
                asyncio.run(
                    client.read_deployment_by_name(
                        f"{underscore_flow_name}/{deployment_name}"
                    )
                )
            )
        except Exception:
            logger.error(
                f"Encountered error while fetching deployment info for `{underscore_flow_name}/{deployment_name}`"
            )
            raise
        args.image_uri = r["job_variables"]["image"]
        args.package_version = extract_tag_value(r["tags"], "PACKAGE_VERSION")
        args.commit_hash = extract_tag_value(r["tags"], "COMMIT_HASH")
        # TODO: note that description, work_pool_name, cron, etc. are set from current version of
        # static config rather than being inherited from source deployment
        deploy(args)


def main_logic(args):
    if args.command == "deploy":
        deploy(args)
    elif args.command == "promote":
        promote(args)
    else:
        raise ValueError(f"Invalid command: {args.command}")


if __name__ == "__main__":
    args = parse_args()
    main_logic(args)
