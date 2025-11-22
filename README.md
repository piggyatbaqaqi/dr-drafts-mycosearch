# Dr. Draft's Mycosearch

State-of-the-art literature search and embedding-based discovery for scientific papers, grant opportunities, and taxonomic data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

Dr. Draft's Mycosearch provides semantic search capabilities for scientific literature and grant opportunities using sentence transformers and embedding-based similarity. Describe what you're looking for in natural language, and the system will find the most relevant papers, grants, or taxonomic records using cosine similarity on semantic embeddings.

### Key Features

- **Semantic Search**: Uses sentence transformers for meaning-based retrieval
- **Multiple Data Sources**: Supports arXiv papers, grants (NSF, NIH, etc.), and taxonomic data
- **CouchDB Integration**: Direct integration with CouchDB for taxonomic data
- **Redis Support**: Store and retrieve embeddings from Redis for scalability
- **CLI and Python API**: Use via command line or integrate into your workflow
- **Multi-GPU Support**: Accelerate embedding computation with multiple GPUs

## Installation

### From PyPI (when published)

```bash
pip install dr-drafts-mycosearch
```

### From Source

```bash
git clone https://github.com/autonlab/dr-drafts-sota-literature-search.git
cd dr-drafts-mycosearch
pip install -e .
```

### With Optional Dependencies

```bash
# Install with CouchDB support
pip install -e .[couchdb]

# Install with all optional features
pip install -e .[all]

# Install for development
pip install -e .[dev]
```

### Using Conda

```bash
conda env create -f env.yml
conda activate drdraft
pip install -e .
```

## Quick Start

### 1. Build the Index

First, build the embeddings index from your data sources:

```bash
dr-drafts-build-index \
  --idir ./index \
  --rdir ./raw \
  --redis-url redis://localhost:6379 \
  --embedding-name myco:embeddings:v1
```

### 2. Search

Search using natural language queries:

```bash
# Search and display to console
dr-drafts -p "machine learning for climate change prediction" -k 5

# Save results to CSV
dr-drafts -p "fungal taxonomy and phylogenetics" -k 10 -o results.csv

# Use Redis for embeddings
dr-drafts \
  --prompt "grant opportunities for AI research" \
  --k 5 \
  --redis-url redis://localhost:6379 \
  --embedding-name myco:embeddings:v1
```

## Usage

### Command Line Interface

```bash
dr-drafts [OPTIONS]

Options:
  -p, --prompt TEXT          Description of what you're looking for
  -k, --k INTEGER           Number of top matches to return (default: 3)
  -o, --output PATH         CSV file to store output
  -t, --title TEXT          Title for results
  --redis-url TEXT          Redis URL (default: redis://localhost:6379)
  --redis-username TEXT     Redis username
  --redis-password TEXT     Redis password
  --redis-db INTEGER        Redis database number (default: 0)
  --embedding-name TEXT     Name of embedding in Redis
  --embeddings-file PATH    Path to local pickle file (alternative to Redis)
```

### Python API

```python
from dr_drafts_mycosearch import Experiment

# Create an experiment
experiment = Experiment(
    prompt="deep learning for medical imaging",
    embeddingsFN=None,  # Use Redis
    k=10,
    redis_url="redis://localhost:6379",
    embedding_name="myco:embeddings:v1"
)

# Run the search
experiment.run()
results = experiment.select_results(range(10))

# Display results
from dr_drafts_mycosearch import results2console
results2console(results)
```

### CouchDB Integration

Load taxonomic data directly from CouchDB:

```python
from dr_drafts_mycosearch.data import COUCHDB

# Connect to CouchDB
couchdb_source = COUCHDB(
    couchdb_url="http://localhost:5984",
    db_name="mycobank_taxa",
    username="admin",
    password="secret"
)

# Get descriptions for embedding
descriptions = couchdb_source.get_descriptions()
print(f"Loaded {len(descriptions)} records")
```

See [COUCHDB_INTEGRATION.md](COUCHDB_INTEGRATION.md) for detailed documentation.

## Data Sources

The system supports multiple data sources:

### Built-in Sources

- **ARXIV**: arXiv papers with abstracts
- **NSF**: National Science Foundation grants
- **GRANTS**: Grants.gov opportunities
- **GFORWARD**: GrantForward database
- **PIVOT**: Proquest PIVOT grants
- **SAM**: SAM.gov contracts
- **SKOL**: Taxonomic data from annotated documents
- **COUCHDB**: Direct CouchDB integration for taxa

### Adding Custom Data

Create a new data class inheriting from `Raw_Data_Index`:

```python
from dr_drafts_mycosearch.data import Raw_Data_Index
import pandas as pd

class MYDATA(Raw_Data_Index):
    def __init__(self, filename: str, desc_att: str):
        super().__init__(filename, desc_att)
        self.load_data()

    def load_data(self):
        self.df = pd.read_csv(self.filename)

    def get_descriptions(self):
        return pd.DataFrame({
            'source': self.__class__.__name__,
            'filename': self.filename,
            'row': self.df.index,
            'description': self.df[self.description_attribute]
        })

    def to_dict(self, idx: int, similarity: float):
        # Convert row to standardized dictionary
        pass
```

## Architecture

### Components

1. **Data Layer** ([src/data.py](src/data.py)): Classes for different data sources
2. **Embeddings** ([src/compute_embeddings.py](src/compute_embeddings.py)): Compute and store embeddings
3. **Search** ([src/sota_search.py](src/sota_search.py)): Similarity search and ranking
4. **Index Builder** ([src/build_index.py](src/build_index.py)): Pipeline for building indices
5. **CLI** ([src/cli.py](src/cli.py)): Command-line interface

### Workflow

```
Data Sources → Extract → Compute Embeddings → Store (Redis/Pickle) → Search → Results
```

## Configuration

### Redis Configuration

Store embeddings in Redis for scalability:

```bash
# Build index with Redis
dr-drafts-build-index \
  --redis-url redis://localhost:6379 \
  --redis-username myuser \
  --redis-password mypass \
  --redis-db 0 \
  --embedding-name myco:embeddings:v1
```

### GPU Configuration

The system automatically detects and uses available GPUs:

- Single GPU: Uses CUDA device 0
- Multiple GPUs: Uses multi-process encoding for faster computation

## Development

### Setup Development Environment

```bash
git clone https://github.com/autonlab/dr-drafts-sota-literature-search.git
cd dr-drafts-mycosearch
pip install -e .[dev]
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
isort src/
flake8 src/
```

## Examples

### Example 1: Search for Papers

```bash
dr-drafts \
  -p "transformer models for natural language processing" \
  -k 10 \
  -o nlp_papers.csv
```

### Example 2: Grant Search

```bash
dr-drafts \
  -p "funding for machine learning research in healthcare" \
  -k 5 \
  --title "ML Healthcare Grants"
```

### Example 3: Taxonomic Search

```bash
dr-drafts \
  -p "novel fungal species from tropical regions" \
  -k 20 \
  --redis-url redis://localhost:6379 \
  --embedding-name taxa:embeddings:v1
```

## Performance

### Embedding Computation

- ~2.5M arXiv abstracts: ~1 hour on GPU
- Multi-GPU support for faster processing
- Batch processing to optimize memory usage

### Search Performance

- Redis-backed: Sub-second queries
- Pickle-backed: 1-2 seconds for large datasets

## Documentation

- [CouchDB Integration Guide](COUCHDB_INTEGRATION.md)
- [Jupyter Usage Guide](src/JUPYTER_USAGE.md)
- [API Documentation](docs/) (coming soon)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Citation

If you use this software in your research, please cite:

```bibtex
@software{drdrafts_mycosearch,
  title = {Dr. Draft's Mycosearch},
  author = {AutonLab},
  year = {2024},
  url = {https://github.com/autonlab/dr-drafts-sota-literature-search}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Sentence Transformers](https://www.sbert.net/)
- Uses the [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) model
- Developed by [AutonLab](https://autonlab.org/)

## Support

- **Issues**: [GitHub Issues](https://github.com/autonlab/dr-drafts-sota-literature-search/issues)
- **Discussions**: [GitHub Discussions](https://github.com/autonlab/dr-drafts-sota-literature-search/discussions)

## Roadmap

- [ ] Web interface
- [ ] More data sources (PubMed, bioRxiv, etc.)
- [ ] Advanced filtering and faceting
- [ ] Citation network analysis
- [ ] Automated paper summarization
- [ ] API server with REST endpoints
