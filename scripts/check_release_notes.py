#!/usr/bin/env python3
"""
Release Notes Validation Script

This script validates that pull requests are properly referenced in the
CHANGELOG.md release notes. It ensures contributors follow the release
notes process described in CONTRIBUTING.md.

Usage:
    python scripts/check_release_notes.py [PR_NUMBER]

When PR_NUMBER is provided, validates that specific PR is referenced.
When run without PR_NUMBER, validates the general format.

Exit codes:
    0 - Success (PR found in release notes or general validation passed)
    1 - Error (PR not found, invalid format, or file access issues)
"""

import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# Configuration
CHANGELOG_PATH = Path(__file__).parent.parent / "CHANGELOG.md"
UNRELEASED_SECTION_REGEX = re.compile(r"## \[Unreleased\]([\s\S]*?)(?=## \[|$)")

# Allow either a PR number like "(#123)" or a commit SHA like "(63ade61)".
# Capture the inner token without the optional leading '#'.
LINK_REGEX = re.compile(r"\(#?([0-9a-fA-F]{7,40}|\d+)\)")


def read_changelog() -> str:
    """Reads and parses the CHANGELOG.md file"""
    try:
        return CHANGELOG_PATH.read_text(encoding="utf-8")
    except Exception as error:
        print(f"❌ Error reading CHANGELOG.md: {error}")
        sys.exit(1)


def extract_unreleased_section(content: str) -> Optional[str]:
    """Extracts the [Unreleased] section from changelog content"""
    match = UNRELEASED_SECTION_REGEX.search(content)
    return match.group(1).strip() if match else None


def extract_references(unreleased_content: str) -> List[str]:
    """Extracts all PR numbers or commit SHAs from the unreleased section as strings"""
    matches = LINK_REGEX.findall(unreleased_content)
    # normalize to lower-case for hex SHAs to make comparisons case-insensitive
    return [m.lower() for m in matches]


def validate_format(unreleased_content: str) -> Tuple[bool, List[str]]:
    """Validates the format of the unreleased section"""
    issues = []

    # Check for valid section headers
    valid_sections = [
        "### Added",
        "### Changed",
        "### Deprecated",
        "### Removed",
        "### Fixed",
        "### Security",
    ]
    has_valid_section = any(section in unreleased_content for section in valid_sections)

    if len(unreleased_content) > 10 and not has_valid_section:
        issues.append(
            "No valid changelog sections found (### Added, ### Changed, ### Fixed, etc.)"
        )

    # Check for entries without references (PR or commit SHA)
    lines = [
        line for line in unreleased_content.split("\n") if line.strip().startswith("-")
    ]
    lines_without_ref = []

    for line in lines:
        # Skip lines that are under historical sections
        if "Historical" in unreleased_content:
            # Find the context around this line to check if it's in a historical section
            line_index = unreleased_content.find(line)
            if line_index > 0:
                before_line = unreleased_content[:line_index]
                last_header_start = before_line.rfind("###")
                if last_header_start >= 0:
                    header_end = unreleased_content.find("\n", last_header_start)
                    if header_end > last_header_start:
                        header_line = unreleased_content[last_header_start:header_end]
                        if "Historical" in header_line:
                            continue  # Skip validation for historical entries

        if not LINK_REGEX.search(line):
            lines_without_ref.append(line.strip())

    if lines_without_ref:
        issues.append(
            f"Found {len(lines_without_ref)} changelog entries without PR/commit references"
        )
        for line in lines_without_ref:
            issues.append(f'  - "{line}"')

    return len(issues) == 0, issues


def validate_release_notes(target: Optional[str] = None) -> None:
    """Main validation function

    target: optional string representing either a PR number (e.g. "42") or a commit SHA (e.g. "63ade61")
    """
    print("🔍 Checking release notes in CHANGELOG.md...\n")

    # Read changelog
    content = read_changelog()
    
    # Check for merge conflict markers that might indicate a problematic merge
    if any(marker in content for marker in ['<<<<<<<', '>>>>>>>', '=======']):
        print("⚠️  Merge conflict markers detected in CHANGELOG.md")
        print("   This usually happens when there are conflicts during PR merge.")
        print("   Please resolve the merge conflicts and ensure the [Unreleased] section is intact.")
        sys.exit(1)
    
    # Extract unreleased section
    unreleased_section = extract_unreleased_section(content)

    if not unreleased_section:
        print("❌ No [Unreleased] section found in CHANGELOG.md")
        print("   Please ensure CHANGELOG.md contains a ## [Unreleased] section")
        print()
        print("💡 This can happen when:")
        print("   - The [Unreleased] section header is missing")
        print("   - There are merge conflicts that removed the section")
        print("   - The file format doesn't match the expected structure")
        print()
        print("   Expected format:")
        print("   ## [Unreleased]")
        print()
        print("   ### Added|Changed|Fixed")
        print("   - **Feature**: Description (#PR_NUMBER)")
        sys.exit(1)

    # If checking for specific PR or commit
    if target:
        target_norm = target.lower()
        references = extract_references(unreleased_section)

        if target_norm in references:
            # Distinguish numeric PR vs commit-like hash for messaging
            if target_norm.isdigit():
                print(f"✅ PR #{target_norm} is properly referenced in release notes")
            else:
                print(
                    f"✅ Commit {target_norm} is properly referenced in release notes"
                )
            print(
                f"📝 Found in [Unreleased] section with {len(references)} total references"
            )
            return
        else:
            if target_norm.isdigit():
                print(
                    f"❌ PR #{target_norm} is NOT referenced in the [Unreleased] section"
                )
            else:
                print(
                    f"❌ Commit {target_norm} is NOT referenced in the [Unreleased] section"
                )
            print("")
            print("Please add an entry to CHANGELOG.md in the [Unreleased] section:")
            print("")
            print("## [Unreleased]")
            print("")
            print("### Added|Changed|Fixed")
            if target_norm.isdigit():
                print(
                    f"- **Your Feature**: Description of your change (#{target_norm})"
                )
            else:
                print(f"- **Your Feature**: Description of your change ({target_norm})")
            print("")
            print("See CONTRIBUTING.md for detailed guidelines.")

            if references:
                display = ", ".join(f"#{r}" if r.isdigit() else r for r in references)
                print(f"\nCurrently referenced: {display}")

            sys.exit(1)

    # General format validation
    success, issues = validate_format(unreleased_section)

    if success:
        references = extract_references(unreleased_section)
        print("✅ Release notes format validation passed")

        if references:
            display = ", ".join(f"#{r}" if r.isdigit() else r for r in references)
            print(f"📝 Found {len(references)} references: {display}")
        else:
            print("📝 [Unreleased] section is empty (this is ok for initial setup)")

        print(
            "\n💡 Tip: Contributors should add their changes to the [Unreleased] section"
        )
        print("   See CONTRIBUTING.md for detailed guidelines")
    else:
        print("❌ Release notes format validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nSee CONTRIBUTING.md for proper release notes format.")
        sys.exit(1)


def main():
    """Main execution"""
    pr_input = None
    if len(sys.argv) > 1:
        pr_input = sys.argv[1].strip()
        # Accept either a numeric PR id or a commit SHA (7-40 hex chars)
        if pr_input.isdigit():
            # numeric PR id
            try:
                if int(pr_input) <= 0:
                    raise ValueError("PR number must be positive")
            except ValueError:
                print(
                    "❌ Invalid PR number provided. Please provide a positive integer."
                )
                sys.exit(1)
        else:
            # validate commit-like hex SHA
            if not re.fullmatch(r"[0-9a-fA-F]{7,40}", pr_input):
                print(
                    "❌ Invalid commit SHA provided. Provide numeric PR id or a 7-40 character hex SHA."
                )
                sys.exit(1)

    validate_release_notes(pr_input)


if __name__ == "__main__":
    main()
