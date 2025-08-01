import argparse
import os
import shutil
from pathlib import Path
import sys
import importlib.util
from typing import Optional


def parse_args():
    parser = argparse.ArgumentParser(
        prog="aps",
        description="SDK to customize behaviour of acme-portal VSCode extension",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add github-copy subcommand
    subparsers.add_parser(
        "github-copy",
        help="Copy GitHub workflow files to .github/workflows in current directory",
    )

    return parser.parse_args()


def get_package_directory(package_name: str) -> Optional[Path]:
    """
    Get the directory path of an installed package.

    Args:
        package_name: Name of the package

    Returns:
        Path to the package directory or None if not found
    """
    spec = importlib.util.find_spec(package_name)
    if spec is None or spec.origin is None:
        return None

    if spec.submodule_search_locations:
        return Path(spec.submodule_search_locations[0])

    return Path(spec.origin).parent


def github_copy() -> bool:
    """
    Copy files from acme_portal_sdk/github/workflows to .github/workflows in the current working directory.
    Fails if a file already exists in the destination.

    Returns:
        bool: True if operation was successful, False otherwise.
    """
    try:
        # Get the package directory
        package_dir = get_package_directory("acme_portal_sdk")
        if package_dir is None:
            print("Error: Could not locate the acme_portal_sdk package.")
            return False

        # Path to the workflows directory in the package
        source_dir = package_dir / "github" / "workflows"

        if not source_dir.exists():
            print(f"Error: Workflows directory not found at {source_dir}")
            return False

        # Create target directory if it doesn't exist
        target_dir = Path(os.getcwd()) / ".github" / "workflows"
        target_dir.mkdir(parents=True, exist_ok=True)

        copied_count = 0
        failed_count = 0

        # Iterate through files in the source directory
        for source_file in source_dir.iterdir():
            if source_file.is_file():
                target_file = target_dir / source_file.name

                # Check if the target file already exists
                if target_file.exists():
                    print(f"Error: File {target_file} already exists. Skipping.")
                    failed_count += 1
                    continue

                # Copy the file
                shutil.copy2(source_file, target_file)
                print(f"Copied: {source_file.name} to {target_file}")
                copied_count += 1

        if failed_count > 0:
            print(
                f"Warning: {failed_count} files could not be copied because they already exist."
            )

        if copied_count > 0:
            print(f"Successfully copied {copied_count} workflow files.")
        else:
            print("No workflow files were found to copy.")

    except PermissionError:
        print("Error: Permission denied when copying files.")
        return False
    except Exception as e:
        print(f"Error during file copy operation: {e}")
        return False

    return True


def main_logic(args):
    if hasattr(args, "command") and args.command == "github-copy":
        if not github_copy():
            sys.exit(1)
    else:
        print("Hello World!")


def main():
    args = parse_args()
    main_logic(args)


if __name__ == "__main__":
    main()
