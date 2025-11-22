# Contributing to Dr. Draft's Mycosearch

Thank you for your interest in contributing to Dr. Draft's Mycosearch! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** (see below)
4. **Create a branch** for your changes
5. **Make your changes**
6. **Test your changes**
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- (Optional) CUDA-capable GPU
- (Optional) Redis server
- (Optional) CouchDB server

### Setup Instructions

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/dr-drafts-sota-literature-search.git
cd dr-drafts-mycosearch
```

2. Add upstream remote:
```bash
git remote add upstream https://github.com/autonlab/dr-drafts-sota-literature-search.git
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install in development mode:
```bash
pip install -e .[dev]
```

5. Install pre-commit hooks (optional but recommended):
```bash
pre-commit install
```

## How to Contribute

### Adding a New Data Source

To add support for a new data source:

1. Create a new class in [src/data.py](src/data.py) that inherits from `Raw_Data_Index`
2. Implement required methods: `load_data()`, `get_descriptions()`, `to_dict()`
3. Add the source name to `DESCRIPTION_ATTR` in [src/compute_embeddings.py](src/compute_embeddings.py)
4. Add tests for your new data source
5. Update documentation

Example:
```python
class NEWSOURCE(Raw_Data_Index):
    def __init__(self, filename: str, desc_att: str):
        super().__init__(filename, desc_att)
        self.load_data()

    def load_data(self):
        # Load data from source
        self.df = pd.read_csv(self.filename)

    def get_descriptions(self):
        return pd.DataFrame({
            'source': self.__class__.__name__,
            'filename': self.filename,
            'row': self.df.index,
            'description': self.df[self.description_attribute]
        })

    def to_dict(self, idx: int, similarity: float):
        # Convert to standard format
        row = self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity'] = similarity
        result['Title'] = row['title']
        # ... add more fields
        return result
```

### Improving Documentation

- Fix typos or clarify existing documentation
- Add examples and use cases
- Improve docstrings
- Add tutorials or guides

### Fixing Bugs

1. Check if the bug is already reported in [Issues](https://github.com/autonlab/dr-drafts-sota-literature-search/issues)
2. If not, create a new issue describing the bug
3. Fork and create a branch: `git checkout -b fix/bug-description`
4. Fix the bug and add tests
5. Submit a pull request

### Adding Features

1. Discuss the feature in an issue first
2. Get consensus from maintainers
3. Fork and create a branch: `git checkout -b feature/feature-name`
4. Implement the feature
5. Add tests and documentation
6. Submit a pull request

## Coding Standards

### Python Style

We follow PEP 8 with some modifications:

- Line length: 100 characters (configured in pyproject.toml)
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Code Formatting

Use the following tools (automatically run by pre-commit):

```bash
# Format code
black src/

# Sort imports
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Documentation

- Use Google-style docstrings
- Include type hints in function signatures
- Add inline comments for complex logic
- Update README.md when adding features

Example docstring:
```python
def search_papers(query: str, k: int = 10) -> pd.DataFrame:
    """Search for papers matching the query.

    Args:
        query: Natural language search query
        k: Number of results to return (default: 10)

    Returns:
        DataFrame with search results containing columns:
            - Title: Paper title
            - Similarity: Similarity score
            - URL: Link to paper

    Raises:
        ValueError: If k is less than 1
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dr_drafts_mycosearch --cov-report=html

# Run specific test file
pytest tests/test_data.py

# Run specific test
pytest tests/test_data.py::test_couchdb_integration
```

### Writing Tests

- Add tests for all new features
- Add tests for bug fixes
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external services (Redis, CouchDB)

Example test:
```python
import pytest
from dr_drafts_mycosearch.data import COUCHDB

def test_couchdb_load():
    """Test loading data from CouchDB."""
    # Setup
    couchdb_source = COUCHDB(
        couchdb_url="http://localhost:5984",
        db_name="test_db"
    )

    # Test
    descriptions = couchdb_source.get_descriptions()

    # Assert
    assert len(descriptions) > 0
    assert 'description' in descriptions.columns
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream changes:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run all tests**:
```bash
pytest
```

3. **Format code**:
```bash
black src/
isort src/
```

4. **Update documentation** if needed

5. **Commit your changes** with clear messages:
```bash
git commit -m "Add: Support for PubMed data source"
```

### Commit Message Guidelines

Use conventional commits:

- `Add: <description>` - New feature
- `Fix: <description>` - Bug fix
- `Docs: <description>` - Documentation changes
- `Refactor: <description>` - Code refactoring
- `Test: <description>` - Adding/updating tests
- `Chore: <description>` - Maintenance tasks

Examples:
```
Add: CouchDB integration for taxonomic data
Fix: Handle empty query strings in search
Docs: Update installation instructions for Redis
Refactor: Simplify embedding computation logic
Test: Add unit tests for data loading
```

### Submitting the Pull Request

1. Push your branch to your fork:
```bash
git push origin your-branch-name
```

2. Go to GitHub and create a pull request

3. Fill out the PR template:
   - Describe what changed
   - Reference related issues
   - Add screenshots if applicable
   - List breaking changes if any

4. Wait for review and address feedback

### Review Process

- Maintainers will review your PR
- You may be asked to make changes
- Once approved, your PR will be merged
- Your contribution will be acknowledged in release notes

## Reporting Bugs

### Before Reporting

1. Check [existing issues](https://github.com/autonlab/dr-drafts-sota-literature-search/issues)
2. Try the latest version
3. Collect information about your environment

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With parameters '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Package version: [e.g., 0.2.0]
- GPU: [if applicable]

**Additional context**
Any other relevant information.
```

## Suggesting Enhancements

### Enhancement Proposal Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots.

**Willingness to contribute**
Are you willing to implement this feature?
```

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search [GitHub Issues](https://github.com/autonlab/dr-drafts-sota-literature-search/issues)
3. Ask in [GitHub Discussions](https://github.com/autonlab/dr-drafts-sota-literature-search/discussions)
4. Contact the maintainers

## Recognition

Contributors will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Credited in academic citations (for significant contributions)

Thank you for contributing to Dr. Draft's Mycosearch!
