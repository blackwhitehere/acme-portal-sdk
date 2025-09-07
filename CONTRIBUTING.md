# Contributing

Thank you for your interest in contributing to acme-portal-sdk! This guide will help you get started with development.

## Development Setup

### Prerequisites

- See pyproject.yml for current minimal supported version of Python. The `.python-version` file used by `uv` contains version of python used for development.
- Git
- GitHub CLI (`gh`) - for workflow testing of acme_portal_sdk.github subpackage

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/blackwhitehere/acme-portal-sdk.git
   cd acme-portal-sdk
   ```

2. **Create development environment**:
   ```bash
   chmod +x create_env.sh
   ./create_env.sh
   source .venv/bin/activate
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Ruff**: For linting and code formatting
- **isort**: For import sorting
- **Pre-commit**: To run checks automatically

Run checks manually:
```bash
# Lint code
ruff check src/

# Format code
ruff format src/

# Sort imports
isort src/
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=acme_portal_sdk

# Check release notes are formatted correctly
python scripts/check_release_notes.py
```

### Documentation

Build documentation locally:
```bash
cd docs
mkdocs build
```
To view it locally
```bash
mkdocs serve
```

## Contributing Guidelines

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write tests for new functionality, mark sections that do not need to be unit tested with `# pragma: no cover` annotation
   - Update documentation `docs/docs/user/api-migration-guide.md` if making API breaking changes
   - Make concise description of added/changed functionality in `user` or `developer` section of the docs depending on the nature of the change
   - Ensure all checks pass

3. **Add Release Notes Entry** (Required):
   - Open `CHANGELOG.md`
   - Add your change to the `[Unreleased]` section
   - Format: `- **Feature Name**: Description (#PR_NUMBER)`
   - See [Release Notes Process](#release-notes-process) below

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create PR through GitHub UI
   ```

### Commit Message Format

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes  
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring

### Code Review

All changes require:
- Passing CI checks (including release notes validation)
- Code review approval
- Documentation updates (if applicable)
- **Release notes entry in CHANGELOG.md**

## Release Notes Process

**Every pull request must include a release notes entry** in `CHANGELOG.md`. This ensures proper documentation of all changes and enables automated release generation.

### Contributing Changes to Release Notes

1. **Add Your Change to CHANGELOG.md**
   - Open `CHANGELOG.md` 
   - Find the `## [Unreleased]` section at the top
   - Add your change under the appropriate subsection:
     - `### Added` - for new features
     - `### Changed` - for changes in existing functionality  
     - `### Deprecated` - for soon-to-be removed features
     - `### Removed` - for now removed features
     - `### Fixed` - for any bug fixes
     - `### Security` - for security-related changes

2. **Format Your Entry**
   ```markdown
   ### Added
   - **Feature Name**: Brief description of the change (#PR_NUMBER)
   ```
   
   **Examples:**
   ```markdown
   ### Added
   - **CLI Progress Display**: Real-time progress updates during deployment operations (#42)
   
   ### Fixed
   - **Configuration Loading**: Fixed issue where environment variables weren't being loaded correctly (#43)
   
   ### Changed
   - **API Response Format**: Improved error response structure for better debugging (#44)
   ```

3. **Link Your Pull Request**
   - Always include the PR number in parentheses: `(#123)`
   - This creates automatic linking and enables automated validation

### Release Notes Validation
- **CI Check**: Automated validation ensures all PRs are referenced in release notes
- **PR Requirements**: Your PR will fail CI if release notes entry is missing
- **Review Process**: Maintainers will verify release notes during code review

### Manual Validation
You can validate your release notes locally:
```bash
# General format validation
python scripts/check_release_notes.py

# Check specific PR reference (after PR is created)
python scripts/check_release_notes.py 123
```

## Version Management

We follow [Semantic Versioning](https://semver.org/):
- Breaking changes increment MAJOR
- New features increment MINOR  
- Bug fixes increment PATCH

## Architecture Overview

The SDK is organized into several modules:

- **Core interfaces**: Abstract base classes for extensibility
- **Prefect implementation**: Concrete implementation for Prefect workflows
- **GitHub integration**: GitHub Actions workflow implementations
- **CLI tools**: Command-line utilities

## Issues and Support

- **Bug reports**: Use GitHub Issues with the bug template
- **Feature requests**: Use GitHub Issues with the feature template
- **Questions**: Start a GitHub Discussion

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.