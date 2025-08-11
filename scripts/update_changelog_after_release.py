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


def read_changelog() -> str:
    """Reads the CHANGELOG.md file"""
    try:
        return CHANGELOG_PATH.read_text(encoding='utf-8')
    except Exception as error:
        print(f"Error reading CHANGELOG.md: {error}", file=sys.stderr)
        sys.exit(1)


def write_changelog(content: str) -> None:
    """Writes content to CHANGELOG.md"""
    try:
        CHANGELOG_PATH.write_text(content, encoding='utf-8')
        print(f"Updated {CHANGELOG_PATH}")
    except Exception as error:
        print(f"Error writing CHANGELOG.md: {error}", file=sys.stderr)
        sys.exit(1)


def update_changelog_for_release(content: str, version: str) -> str:
    """Updates changelog content for the new release"""
    # Get current date in ISO format
    release_date = datetime.now().strftime("%Y-%m-%d")
    
    # Find the [Unreleased] section
    unreleased_pattern = re.compile(r"(## \[Unreleased\][^\n]*\n)([\s\S]*?)(?=## \[|$)", re.IGNORECASE)
    match = unreleased_pattern.search(content)
    
    if not match:
        print("Error: No [Unreleased] section found in CHANGELOG.md", file=sys.stderr)
        sys.exit(1)
    
    unreleased_header = match.group(1)
    unreleased_content = match.group(2).strip()
    
    # If unreleased section is empty, provide a default entry
    if not unreleased_content:
        unreleased_content = "### Changed\n- Version release"
    
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
    
    print(f"Updating CHANGELOG.md for release {version}")
    
    # Read current changelog
    content = read_changelog()
    
    # Check if version already exists
    version_pattern = re.compile(rf"## \[{re.escape(version)}\]", re.IGNORECASE)
    if version_pattern.search(content):
        print(f"Warning: Version {version} already exists in CHANGELOG.md")
        print("Skipping changelog update.")
        return
    
    # Update the changelog
    updated_content = update_changelog_for_release(content, version)
    
    # Write back to file
    write_changelog(updated_content)
    
    print(f"Successfully updated CHANGELOG.md:")
    print(f"- Moved [Unreleased] content to [{version}] section")
    print(f"- Created new empty [Unreleased] section")


if __name__ == "__main__":
    main()