# Dr. Draft's Mycosearch - Project Structure

This document describes the complete structure of the dr-drafts-mycosearch Python package.

## Overview

Dr. Draft's Mycosearch is now a fully-packaged Python project with modern packaging standards, CLI tools, and comprehensive documentation.

## Package Information

- **Name**: `dr-drafts-mycosearch`
- **Version**: `0.2.0`
- **License**: MIT
- **Python**: >=3.8
- **Package Name**: `dr_drafts_mycosearch` (importable)

## Directory Structure

```
dr-drafts-mycosearch/
│
├── src/                          # Main source code (package: dr_drafts_mycosearch)
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # CLI entry point (dr-drafts command)
│   ├── data.py                  # Data source classes (NSF, ARXIV, COUCHDB, etc.)
│   ├── sota_search.py           # Search engine and similarity computation
│   ├── compute_embeddings.py   # Embedding computation with sentence transformers
│   ├── build_index.py          # Index building pipeline (dr-drafts-build-index command)
│   ├── xml2csv.py              # XML to CSV conversion utilities
│   ├── test_data.py            # Data loading tests
│   ├── example_couchdb_usage.py # CouchDB integration example
│   ├── get_skol.sh             # Script to fetch SKOL data
│   ├── JUPYTER_USAGE.md        # Jupyter notebook guide
│   └── __pycache__/            # Python cache (ignored by git)
│
├── prompts/                     # Example search prompts
│   ├── cli_sample.sh
│   └── csv_sample.sh
│
├── index/                       # Generated embeddings (ignored by git)
│   └── embeddings.pkl          # Pickled embeddings (if not using Redis)
│
├── raw/                         # Raw data files (ignored by git)
│   └── [symlink to SKOL data]
│
├── Documentation Files
│   ├── README.md               # Main documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── INSTALL.md             # Detailed installation instructions
│   ├── CONTRIBUTING.md        # Contribution guidelines
│   ├── COUCHDB_INTEGRATION.md # CouchDB integration guide
│   ├── PROJECT_STRUCTURE.md   # This file
│   └── LICENSE                # MIT license
│
├── Configuration Files
│   ├── pyproject.toml         # Modern Python packaging (PEP 621)
│   ├── setup.py               # Backward-compatible setup
│   ├── MANIFEST.in            # Package data inclusion rules
│   ├── requirements.txt       # Core dependencies
│   ├── requirements-optional.txt # Optional dependencies (CouchDB, Kaggle)
│   ├── requirements-dev.txt   # Development dependencies
│   ├── env.yml                # Conda environment
│   └── .gitignore             # Git ignore rules
│
├── Legacy/Compatibility
│   ├── main.py                # Legacy CLI (uses src.sota_search)
│   ├── __init__.py            # Root package marker
│   └── test.sh                # Test script
│
└── Git
    ├── .git/                  # Git repository
    └── .gitignore             # Ignore patterns

```

## Python Package Structure

### Importable Package: `dr_drafts_mycosearch`

```python
# Main classes and functions
from dr_drafts_mycosearch import Experiment, EmbeddingsComputer, IndexBuilder
from dr_drafts_mycosearch import results2console, results2csv

# Data sources module
from dr_drafts_mycosearch import data
from dr_drafts_mycosearch.data import COUCHDB, NSF, ARXIV, SKOL, etc.
```

### CLI Commands

Two CLI entry points are installed:

1. **`dr-drafts`** - Main search interface
   - Defined in: `src/cli.py:main()`
   - Usage: `dr-drafts -p "query" -k 5`

2. **`dr-drafts-build-index`** - Index building tool
   - Defined in: `src/build_index.py:main()`
   - Usage: `dr-drafts-build-index --redis-url redis://localhost:6379`

## Core Components

### 1. Data Layer (`src/data.py`)

Contains classes for different data sources, all inheriting from `Raw_Data_Index`:

- **COUCHDB**: Direct CouchDB integration for taxonomic data
- **SKOL**: Taxonomic data from annotated documents
- **ARXIV**: arXiv papers
- **NSF**: National Science Foundation grants
- **GRANTS**: Grants.gov opportunities
- **GFORWARD**: GrantForward database
- **PIVOT**: Proquest PIVOT grants
- **SAM**: SAM.gov contracts
- **SCS**: SCS Resources
- **CMU**: CMU Foundation Relations
- **EXTERNAL**: External funding sources

Each class implements:
- `load_data()`: Load data from source
- `get_descriptions()`: Extract descriptions for embedding
- `to_dict(idx, similarity)`: Convert to standard display format
- `date2MMDDYYYY(date)`: Date formatting

### 2. Embeddings (`src/compute_embeddings.py`)

**Class: `EmbeddingsComputer`**

Computes semantic embeddings using sentence transformers:
- Model: `all-mpnet-base-v2`
- Multi-GPU support
- Redis and pickle storage
- Batch processing

Key methods:
- `encode_narratives(N)`: Encode text to embeddings
- `write_embeddings_to_redis()`: Store in Redis
- `write_embeddings_to_file()`: Store as pickle

### 3. Search Engine (`src/sota_search.py`)

**Class: `Experiment`**

Performs similarity search using cosine similarity:
- Loads embeddings from Redis or pickle
- Encodes search queries
- Computes similarity scores
- Returns ranked results

Key methods:
- `run()`: Execute search
- `select_results(range)`: Get top-k results
- `results2console()`: Display results
- `results2csv()`: Save to CSV

### 4. Index Builder (`src/build_index.py`)

**Class: `IndexBuilder`**

Orchestrates the index building pipeline:
- Creates necessary directories
- Runs data preparation scripts
- Computes embeddings
- Stores in Redis or pickle

### 5. CLI Interface (`src/cli.py`)

Command-line interface for search:
- Argument parsing
- Redis/pickle configuration
- Result formatting
- Error handling

## Configuration Files

### `pyproject.toml`

Modern Python packaging (PEP 621):
- Project metadata
- Dependencies (core, optional, dev)
- CLI entry points
- Build system configuration
- Tool configurations (black, mypy, pytest)

### `setup.py`

Backward compatibility for older pip versions:
- Minimal wrapper around pyproject.toml
- Delegates to setuptools build backend

### `MANIFEST.in`

Package data inclusion:
- Documentation files
- Shell scripts
- Example prompts
- Excludes: build artifacts, caches, data directories

## Installation Methods

### 1. Development Installation
```bash
pip install -e .          # Basic
pip install -e .[couchdb] # With CouchDB
pip install -e .[dev]     # With dev tools
pip install -e .[all]     # Everything
```

### 2. Production Installation (when published)
```bash
pip install dr-drafts-mycosearch
pip install dr-drafts-mycosearch[couchdb]
```

### 3. From Requirements Files
```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
pip install -r requirements-dev.txt
```

## Dependencies

### Core Dependencies
- pandas >=2.0.3
- numpy >=1.24.4
- torch >=2.4.0
- sentence-transformers >=3.0.1
- transformers >=4.44.0
- scikit-learn >=1.0.0
- redis >=4.0.0
- requests >=2.32.3
- python-dateutil >=2.9.0
- regex >=2024.7.24

### Optional Dependencies
- couchdb >=1.2 (for CouchDB integration)
- kaggle >=1.6.17 (for Kaggle datasets)

### Development Dependencies
- pytest >=7.0.0
- pytest-cov >=4.0.0
- black >=23.0.0
- flake8 >=6.0.0
- mypy >=1.0.0
- isort >=5.0.0

## Data Flow

```
┌─────────────────┐
│  Data Sources   │
│ (CSV, CouchDB)  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Data Classes   │
│   (data.py)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Embeddings    │
│ (sentence-bert) │
└────────┬────────┘
         │
         v
┌─────────────────┐
│     Storage     │
│ (Redis/Pickle)  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Search Engine  │
│ (cosine sim.)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│    Results      │
│ (Console/CSV)   │
└─────────────────┘
```

## Testing

### Test Organization
- Unit tests: `tests/test_*.py`
- Integration tests: `tests/integration/`
- Test data: `tests/fixtures/`

### Running Tests
```bash
pytest                          # All tests
pytest --cov=dr_drafts_mycosearch  # With coverage
pytest tests/test_data.py       # Specific test file
```

## Documentation Files

1. **README.md** - Main project documentation
2. **QUICKSTART.md** - 5-minute getting started guide
3. **INSTALL.md** - Detailed installation instructions
4. **CONTRIBUTING.md** - Contribution guidelines
5. **COUCHDB_INTEGRATION.md** - CouchDB integration guide
6. **PROJECT_STRUCTURE.md** - This file
7. **src/JUPYTER_USAGE.md** - Jupyter notebook usage

## Version History

- **0.2.0** (Current)
  - Converted to proper Python package
  - Added CLI entry points
  - CouchDB integration
  - Redis support
  - Comprehensive documentation

- **0.1.0** (Original)
  - Basic literature search
  - arXiv integration
  - Local pickle storage

## Future Enhancements

See README.md Roadmap section for planned features.

## Maintenance

### Updating Version
1. Update version in `pyproject.toml`
2. Update `__version__` in `src/__init__.py`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`

### Publishing to PyPI
```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Support

For questions or issues:
- GitHub Issues: https://github.com/autonlab/dr-drafts-sota-literature-search/issues
- Documentation: See README.md and other .md files
