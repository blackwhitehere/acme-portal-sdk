When possible make code easy to change in the future.
Isolate distinct concerns into distinct components because that makes code easy to change.
Create components with single reponsibilities because that makes them easy to change.
Name things well becasue that makes code easy to read and make changes to.
Allow for design decisions to be reversed because that makes code easy to change when new requirements arrive.

Adhere to DRY (don't repeat yourself) principle if possible. Centralize definition of the same knowledge and use it in all places it's used. When possible attempt to refactor code to obey this principle.

Design systems to have orthogonal functionality.

Check for python typing information in method signatures is correct and if documentation needs to be updated to reflect existing funcionality.

## Documentation Style

Write documentation that is very direct and verbose. Detailed when needed but not explain too much extra context:
- Use clear, simple language
- Be comprehensive and detailed when information is needed
- Focus on what users need to do, not why or how it works internally
- Avoid redundant information and unnecessary context
- Keep code comments minimal - only explain complex logic, not obvious actions

## Release Notes Requirements

**Every pull request must include a release notes entry in CHANGELOG.md**

When making changes:
1. **Always add an entry to the `[Unreleased]` section** in CHANGELOG.md
2. **Use the appropriate category**:
   - `### Added` - for new features
   - `### Changed` - for changes in existing functionality  
   - `### Fixed` - for bug fixes
   - `### Security` - for security-related changes
   - `### Deprecated` - for soon-to-be removed features
   - `### Removed` - for removed features

3. **Format entries correctly**:
   ```markdown
   - **Feature/Fix Name**: Brief description of the change (#PR_NUMBER)
   ```

4. **Include PR reference**: Always add the PR number in parentheses for linking
5. **Make it user-focused**: Describe the change from the user's perspective, not implementation details

**Example entry:**
```markdown
### Added
- **Deploy Progress Notifications**: Added real-time progress updates during flow deployment operations (#42)
```

See docs/docs/developer/contributing.md for complete release notes guidelines.