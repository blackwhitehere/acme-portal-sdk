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

#### Documentation Style

Write documentation that is very direct and verbose. Detailed when needed but not explain too much extra context:
- Use clear, simple language
- Be comprehensive and detailed when information is needed
- Focus on what users need to do, not why or how it works internally
- Avoid redundant information and unnecessary context
- Keep code comments minimal - only explain complex logic, not obvious actions

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

**Every PR must include a release notes entry** in `CHANGELOG.md`.

### Adding Release Notes

1. **Edit CHANGELOG.md**
   - Find the `## [Unreleased]` section
   - Add your change under the appropriate category:
     - `### Added` - new features
     - `### Changed` - functionality changes  
     - `### Fixed` - bug fixes
     - `### Security` - security updates

2. **Format Entry**
   ```markdown
   ### Added
   - **Feature Name**: Brief description (#PR_NUMBER)
   ```

3. **Include PR Reference**
   - Always add PR number: `(#123)`
   - Enables automatic validation

### Validation
```bash
python scripts/check_release_notes.py [PR_NUMBER]
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