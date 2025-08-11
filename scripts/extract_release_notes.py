#!/usr/bin/env python3
"""
Release Notes Extractor Script

This script extracts release notes from CHANGELOG.md for a specific version
or the [Unreleased] section for use in GitHub releases.

Usage:
    python scripts/extract_release_notes.py [VERSION]

When VERSION is provided (e.g., "1.0.0"), extracts notes for that version.
When run without VERSION, extracts the [Unreleased] section.

Output is formatted for GitHub releases with proper markdown.
"""

import re
import sys
from pathlib import Path
from typing import Optional


# Configuration
CHANGELOG_PATH = Path(__file__).parent.parent / "CHANGELOG.md"


def read_changelog() -> str:
    """Reads and parses the CHANGELOG.md file"""
    try:
        return CHANGELOG_PATH.read_text(encoding='utf-8')
    except Exception as error:
        print(f"Error reading CHANGELOG.md: {error}", file=sys.stderr)
        sys.exit(1)


def extract_release_notes(content: str, version: Optional[str] = None) -> Optional[str]:
    """Extracts release notes for a specific version or unreleased section"""
    if version:
        # Match specific version section
        version_escaped = re.escape(version)
        pattern = re.compile(rf"## \[{version_escaped}\][^\n]*\n([\s\S]*?)(?=## \[|$)", re.IGNORECASE)
    else:
        # Match unreleased section
        pattern = re.compile(r"## \[Unreleased\][^\n]*\n([\s\S]*?)(?=## \[|$)", re.IGNORECASE)
    
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def format_for_github(raw_notes: str, version: Optional[str] = None) -> str:
    """Formats release notes for GitHub release"""
    # Clean up the notes
    lines = [line.strip() for line in raw_notes.split('\n') if line.strip()]
    formatted = '\n'.join(lines)
    
    # If it's empty, provide a default message
    if not formatted:
        if version:
            return f"Release {version}\n\nSee CHANGELOG.md for details."
        else:
            return "No release notes available.\n\nSee CHANGELOG.md for details."
    
    # Add header if it's from unreleased section
    if not version:
        formatted = f"Release Notes\n\n{formatted}"
    
    return formatted


def extract_for_release(version: Optional[str] = None) -> None:
    """Main extraction function"""
    content = read_changelog()
    raw_notes = extract_release_notes(content, version)
    
    if not raw_notes:
        if version:
            print(f"No release notes found for version {version}", file=sys.stderr)
            print("Available versions in CHANGELOG.md:", file=sys.stderr)
            
            # Show available versions
            version_matches = re.findall(r"## \[[^\]]+\]", content)
            if version_matches:
                for match in version_matches:
                    print(f"  - {match}", file=sys.stderr)
        else:
            print("No [Unreleased] section found in CHANGELOG.md", file=sys.stderr)
        sys.exit(1)
    
    formatted = format_for_github(raw_notes, version)
    print(formatted)


def main():
    """Main execution"""
    version = sys.argv[1] if len(sys.argv) > 1 else None
    extract_for_release(version)


if __name__ == "__main__":
    main()