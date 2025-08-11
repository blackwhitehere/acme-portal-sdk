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
PR_LINK_REGEX = re.compile(r"\(#(\d+)\)")


def read_changelog() -> str:
    """Reads and parses the CHANGELOG.md file"""
    try:
        return CHANGELOG_PATH.read_text(encoding='utf-8')
    except Exception as error:
        print(f"❌ Error reading CHANGELOG.md: {error}")
        sys.exit(1)


def extract_unreleased_section(content: str) -> Optional[str]:
    """Extracts the [Unreleased] section from changelog content"""
    match = UNRELEASED_SECTION_REGEX.search(content)
    return match.group(1).strip() if match else None


def extract_pr_numbers(unreleased_content: str) -> List[int]:
    """Extracts all PR numbers from the unreleased section"""
    matches = PR_LINK_REGEX.findall(unreleased_content)
    return [int(match) for match in matches]


def validate_format(unreleased_content: str) -> Tuple[bool, List[str]]:
    """Validates the format of the unreleased section"""
    issues = []
    
    # Check for valid section headers
    valid_sections = ['### Added', '### Changed', '### Deprecated', '### Removed', '### Fixed', '### Security']
    has_valid_section = any(section in unreleased_content for section in valid_sections)
    
    if len(unreleased_content) > 10 and not has_valid_section:
        issues.append('No valid changelog sections found (### Added, ### Changed, ### Fixed, etc.)')
    
    # Check for entries without PR links (but ignore historical sections)
    lines = [line for line in unreleased_content.split('\n') if line.strip().startswith('-')]
    lines_without_pr = []
    
    for line in lines:
        # Skip lines that are under historical sections
        if 'Historical' in unreleased_content:
            # Find the context around this line to check if it's in a historical section
            line_index = unreleased_content.find(line)
            if line_index > 0:
                before_line = unreleased_content[:line_index]
                last_header_start = before_line.rfind('###')
                if last_header_start >= 0:
                    header_end = unreleased_content.find('\n', last_header_start)
                    if header_end > last_header_start:
                        header_line = unreleased_content[last_header_start:header_end]
                        if 'Historical' in header_line:
                            continue  # Skip validation for historical entries
        
        if not PR_LINK_REGEX.search(line):
            lines_without_pr.append(line.strip())
    
    if lines_without_pr:
        issues.append(f"Found {len(lines_without_pr)} changelog entries without PR references")
        for line in lines_without_pr:
            issues.append(f"  - \"{line}\"")
    
    return len(issues) == 0, issues


def validate_release_notes(target_pr: Optional[int] = None) -> None:
    """Main validation function"""
    print("🔍 Checking release notes in CHANGELOG.md...\n")
    
    # Read changelog
    content = read_changelog()
    
    # Extract unreleased section
    unreleased_section = extract_unreleased_section(content)
    
    if not unreleased_section:
        print("❌ No [Unreleased] section found in CHANGELOG.md")
        print("   Please ensure CHANGELOG.md contains a ## [Unreleased] section")
        sys.exit(1)
    
    # If checking for specific PR
    if target_pr:
        pr_numbers = extract_pr_numbers(unreleased_section)
        
        if target_pr in pr_numbers:
            print(f"✅ PR #{target_pr} is properly referenced in release notes")
            print(f"📝 Found in [Unreleased] section with {len(pr_numbers)} total PR references")
            return
        else:
            print(f"❌ PR #{target_pr} is NOT referenced in the [Unreleased] section")
            print("")
            print("Please add an entry to CHANGELOG.md in the [Unreleased] section:")
            print("")
            print("## [Unreleased]")
            print("")
            print("### Added|Changed|Fixed")
            print(f"- **Your Feature**: Description of your change (#{target_pr})")
            print("")
            print("See CONTRIBUTING.md for detailed guidelines.")
            
            if pr_numbers:
                print(f"\nCurrently referenced PRs: {', '.join(f'#{n}' for n in pr_numbers)}")
            
            sys.exit(1)
    
    # General format validation
    success, issues = validate_format(unreleased_section)
    
    if success:
        pr_numbers = extract_pr_numbers(unreleased_section)
        print("✅ Release notes format validation passed")
        
        if pr_numbers:
            print(f"📝 Found {len(pr_numbers)} PR references: {', '.join(f'#{n}' for n in pr_numbers)}")
        else:
            print("📝 [Unreleased] section is empty (this is ok for initial setup)")
        
        print("\n💡 Tip: Contributors should add their changes to the [Unreleased] section")
        print("   See CONTRIBUTING.md for detailed guidelines")
    else:
        print("❌ Release notes format validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nSee CONTRIBUTING.md for proper release notes format.")
        sys.exit(1)


def main():
    """Main execution"""
    pr_number = None
    if len(sys.argv) > 1:
        try:
            pr_number = int(sys.argv[1])
            if pr_number <= 0:
                raise ValueError("PR number must be positive")
        except ValueError:
            print("❌ Invalid PR number provided. Please provide a positive integer.")
            sys.exit(1)
    
    validate_release_notes(pr_number)


if __name__ == "__main__":
    main()