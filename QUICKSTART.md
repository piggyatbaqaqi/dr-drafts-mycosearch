# Quick Start Guide

Get started with Dr. Draft's Mycosearch in 5 minutes.

## Installation

```bash
# Clone repository
git clone https://github.com/autonlab/dr-drafts-sota-literature-search.git
cd dr-drafts-mycosearch

# Install
pip install -e .

# With CouchDB support
pip install -e .[couchdb]
```

## Basic Usage

### 1. Build Index

```bash
# Build index with Redis (recommended)
dr-drafts-build-index \
  --redis-url redis://localhost:6379 \
  --embedding-name myco:embeddings:v1

# Or build with local pickle file
dr-drafts-build-index --idir ./index
```

### 2. Search

```bash
# Basic search
dr-drafts -p "your search query" -k 5

# Save to CSV
dr-drafts -p "machine learning for healthcare" -k 10 -o results.csv

# With Redis
dr-drafts \
  -p "your query" \
  -k 5 \
  --redis-url redis://localhost:6379 \
  --embedding-name myco:embeddings:v1
```

## Python API

```python
from dr_drafts_mycosearch import Experiment, results2console

# Create experiment
experiment = Experiment(
    prompt="deep learning for NLP",
    embeddingsFN=None,  # Use Redis
    k=10,
    redis_url="redis://localhost:6379",
    embedding_name="myco:embeddings:v1"
)

# Run search
experiment.run()
results = experiment.select_results(range(10))

# Display results
results2console(results)
```

## CouchDB Integration

```python
from dr_drafts_mycosearch.data import SKOL_TAXA

# Connect to CouchDB
source = SKOL_TAXA(
    couchdb_url="http://localhost:5984",
    db_name="taxa_db"
)

# Get descriptions
descriptions = source.get_descriptions()
```

## Common Commands

```bash
# Show help
dr-drafts --help
dr-drafts-build-index --help

# Test installation
python -c "from dr_drafts_mycosearch import Experiment; print('OK')"

# Check GPU
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Test Redis
redis-cli ping
```

## Directory Structure

```
dr-drafts-mycosearch/
├── src/                 # Source code
│   ├── data.py         # Data sources
│   ├── sota_search.py  # Search engine
│   ├── compute_embeddings.py
│   ├── build_index.py
│   └── cli.py          # CLI interface
├── index/              # Generated embeddings
├── raw/                # Raw data
├── prompts/            # Example prompts
├── pyproject.toml      # Package configuration
├── README.md           # Full documentation
└── INSTALL.md          # Installation guide
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [INSTALL.md](INSTALL.md) for installation troubleshooting
- See [COUCHDB_INTEGRATION.md](COUCHDB_INTEGRATION.md) for CouchDB guide
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Getting Help

- **Documentation**: See README.md
- **Issues**: https://github.com/autonlab/dr-drafts-sota-literature-search/issues
- **Installation problems**: See INSTALL.md

## Examples

### Search arXiv Papers
```bash
dr-drafts -p "quantum computing algorithms" -k 10 -o quantum.csv
```

### Search Grants
```bash
dr-drafts -p "funding for climate change research" -k 5
```

### Search Taxonomic Data
```bash
dr-drafts -p "novel fungal species" -k 20 --embedding-name taxa:v1
```

That's it! You're ready to use Dr. Draft's Mycosearch.
