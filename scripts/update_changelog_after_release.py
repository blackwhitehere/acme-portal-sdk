#!/usr/bin/env python3
"""
Changelog Update Script for Post-Release

This script automatically updates CHANGELOG.md after a release by:
1. Moving [Unreleased] content to a new versioned section
2. Creating a fresh [Unreleased] section for future changes
3. Adding the release date to the new version section

Usage:
    python scripts/update_changelog_after_release.py VERSION

Example:
    python scripts/update_changelog_after_release.py 1.0.0
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List


# Configuration
CHANGELOG_PATH = Path(__file__).parent.parent / "CHANGELOG.md"
API_MIGRATION_GUIDE_PATH = Path(__file__).parent.parent / "docs" / "docs" / "user" / "api-migration-guide.md"


def read_file(file_path: Path) -> str:
    """Reads a file"""
    try:
        return file_path.read_text(encoding='utf-8')
    except Exception as error:
        print(f"Error reading {file_path}: {error}", file=sys.stderr)
        sys.exit(1)


def write_file(file_path: Path, content: str) -> None:
    """Writes content to a file"""
    try:
        file_path.write_text(content, encoding='utf-8')
        print(f"Updated {file_path}")
    except Exception as error:
        print(f"Error writing {file_path}: {error}", file=sys.stderr)
        sys.exit(1)


def read_changelog() -> str:
    """Reads the CHANGELOG.md file"""
    return read_file(CHANGELOG_PATH)


def write_changelog(content: str) -> None:
    """Writes content to CHANGELOG.md"""
    write_file(CHANGELOG_PATH, content)


def read_api_migration_guide() -> str:
    """Reads the api-migration-guide.md file"""
    return read_file(API_MIGRATION_GUIDE_PATH)


def write_api_migration_guide(content: str) -> None:
    """Writes content to api-migration-guide.md"""
    write_file(API_MIGRATION_GUIDE_PATH, content)


def update_file_for_release(content: str, version: str, file_type: str) -> str:
    """Updates file content for the new release"""
    # Get current date in ISO format
    release_date = datetime.now().strftime("%Y-%m-%d")
    
    # Find the [Unreleased] section
    unreleased_pattern = re.compile(r"(## \[Unreleased\][^\n]*\n)([\s\S]*?)(?=## \[|$)", re.IGNORECASE)
    match = unreleased_pattern.search(content)
    
    if not match:
        print(f"Error: No [Unreleased] section found in {file_type}", file=sys.stderr)
        sys.exit(1)
    
    unreleased_header = match.group(1)
    unreleased_content = match.group(2).strip()
    
    # If unreleased section is empty, provide a default entry
    if not unreleased_content:
        if file_type == "CHANGELOG.md":
            unreleased_content = "### Changed\n- Version release"
        else:  # api-migration-guide.md
            unreleased_content = "### Changes\n- Version release"
    
    # Create the new version section
    new_version_section = f"## [{version}] - {release_date}\n\n{unreleased_content}\n\n"
    
    # Create new empty unreleased section
    new_unreleased_section = "## [Unreleased]\n\n"
    
    # Replace the [Unreleased] section with new unreleased + new version sections
    updated_content = unreleased_pattern.sub(
        new_unreleased_section + new_version_section,
        content
    )
    
    return updated_content


def update_changelog_for_release(content: str, version: str) -> str:
    """Updates changelog content for the new release"""
    return update_file_for_release(content, version, "CHANGELOG.md")


def update_api_migration_guide_for_release(content: str, version: str) -> str:
    """Updates api-migration-guide content for the new release"""
    return update_file_for_release(content, version, "api-migration-guide.md")


def main():
    """Main execution"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_changelog_after_release.py VERSION", file=sys.stderr)
        print("Example: python scripts/update_changelog_after_release.py 1.0.0", file=sys.stderr)
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Remove 'v' prefix if present
    if version.startswith('v'):
        version = version[1:]
    
    print(f"Updating CHANGELOG.md and api-migration-guide.md for release {version}")
    
    # Read current changelog
    changelog_content = read_changelog()
    
    # Check if version already exists in changelog
    version_pattern = re.compile(rf"## \[{re.escape(version)}\]", re.IGNORECASE)
    if version_pattern.search(changelog_content):
        print(f"Warning: Version {version} already exists in CHANGELOG.md")
        print("Skipping changelog update.")
        return
    
    # Update the changelog
    updated_changelog_content = update_changelog_for_release(changelog_content, version)
    
    # Write back to changelog file
    write_changelog(updated_changelog_content)
    
    # Read and update api-migration-guide.md
    if API_MIGRATION_GUIDE_PATH.exists():
        api_guide_content = read_api_migration_guide()
        
        # Check if version already exists in api guide
        if version_pattern.search(api_guide_content):
            print(f"Warning: Version {version} already exists in api-migration-guide.md")
            print("Skipping api-migration-guide.md update.")
        else:
            # Update the api migration guide
            updated_api_guide_content = update_api_migration_guide_for_release(api_guide_content, version)
            
            # Write back to api guide file
            write_api_migration_guide(updated_api_guide_content)
            
            print(f"Successfully updated api-migration-guide.md:")
            print(f"- Moved [Unreleased] content to [{version}] section")
            print(f"- Created new empty [Unreleased] section")
    else:
        print("Warning: api-migration-guide.md not found, skipping its update")
    
    print(f"Successfully updated CHANGELOG.md:")
    print(f"- Moved [Unreleased] content to [{version}] section")
    print(f"- Created new empty [Unreleased] section")


if __name__ == "__main__":
    main()