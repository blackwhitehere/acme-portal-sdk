"""Python version compatibility detection and validation utilities."""

import sys
from typing import Optional, Tuple


def get_python_version() -> Tuple[int, int, int]:
    """Get the current Python version as a tuple of (major, minor, micro).
    
    Returns:
        Tuple[int, int, int]: The Python version tuple (e.g., (3, 9, 0))
    """
    return sys.version_info[:3]


def get_required_python_version() -> Tuple[int, int]:
    """Get the minimum required Python version for this package.
    
    Returns:
        Tuple[int, int]: The minimum required version tuple (e.g., (3, 9))
    """
    return (3, 9)


def is_python_version_compatible(min_version: Optional[Tuple[int, int]] = None) -> bool:
    """Check if the current Python version meets the minimum requirements.
    
    Args:
        min_version: Optional minimum version tuple. Defaults to package requirement.
        
    Returns:
        bool: True if the current Python version is compatible, False otherwise.
    """
    if min_version is None:
        min_version = get_required_python_version()
    
    current_version = get_python_version()[:2]  # Only compare major.minor
    return current_version >= min_version


def get_version_info_message() -> str:
    """Get a formatted message with current and required Python version information.
    
    Returns:
        str: A formatted message describing version compatibility.
    """
    current = get_python_version()
    required = get_required_python_version()
    is_compatible = is_python_version_compatible()
    
    current_str = f"{current[0]}.{current[1]}.{current[2]}"
    required_str = f"{required[0]}.{required[1]}+"
    
    status = "✓ Compatible" if is_compatible else "✗ Incompatible"
    
    return (
        f"Python Version Check:\n"
        f"  Current version: {current_str}\n"
        f"  Required version: {required_str}\n"
        f"  Status: {status}"
    )


def check_compatibility_and_warn() -> bool:
    """Check Python version compatibility and print warnings if incompatible.
    
    Returns:
        bool: True if compatible, False if incompatible.
        
    Side effects:
        Prints warning messages to stderr if incompatible.
    """
    if not is_python_version_compatible():
        current = get_python_version()
        required = get_required_python_version()
        
        print(
            f"WARNING: Incompatible Python version detected!\n"
            f"Current: {current[0]}.{current[1]}.{current[2]}\n"
            f"Required: {required[0]}.{required[1]}+\n"
            f"Please upgrade your Python version to avoid compatibility issues.",
            file=sys.stderr
        )
        return False
    return True


def main():
    """Command-line interface for Python version checking."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Check Python version compatibility for acme-portal-sdk"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output compatibility status (compatible/incompatible)"
    )
    parser.add_argument(
        "--exit-code",
        action="store_true", 
        help="Exit with non-zero code if incompatible"
    )
    
    args = parser.parse_args()
    
    is_compatible = is_python_version_compatible()
    
    if args.quiet:
        print("compatible" if is_compatible else "incompatible")
    else:
        print(get_version_info_message())
    
    if args.exit_code and not is_compatible:
        sys.exit(1)


if __name__ == "__main__":
    main()