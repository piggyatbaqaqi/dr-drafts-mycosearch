# Installation Guide

This guide provides detailed installation instructions for Dr. Draft's Mycosearch.

## Prerequisites

- Python 3.8 or higher
- pip or conda package manager
- (Optional) CUDA-compatible GPU for faster embedding computation
- (Optional) Redis server for scalable embedding storage
- (Optional) CouchDB for taxonomic data integration

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. **Clone the repository**

```bash
git clone https://github.com/autonlab/dr-drafts-sota-literature-search.git
cd dr-drafts-mycosearch
```

2. **Create a virtual environment** (recommended)

Using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Using conda:
```bash
conda env create -f env.yml
conda activate drdraft
```

3. **Install the package**

Basic installation:
```bash
pip install -e .
```

With CouchDB support:
```bash
pip install -e .[couchdb]
```

With all optional dependencies:
```bash
pip install -e .[all]
```

For development (includes testing and linting tools):
```bash
pip install -e .[dev]
```

### Method 2: Install from PyPI (When Available)

```bash
pip install dr-drafts-mycosearch

# With optional dependencies
pip install dr-drafts-mycosearch[couchdb]
pip install dr-drafts-mycosearch[all]
```

### Method 3: Install Using Requirements Files

```bash
# Clone repository
git clone https://github.com/autonlab/dr-drafts-sota-literature-search.git
cd dr-drafts-mycosearch

# Install core dependencies
pip install -r requirements.txt

# Install optional dependencies
pip install -r requirements-optional.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in editable mode
pip install -e .
```

## Verify Installation

Test that the installation was successful:

```bash
# Test CLI commands
dr-drafts --help
dr-drafts-build-index --help

# Test Python API
python -c "from dr_drafts_mycosearch import Experiment; print('Success!')"
```

## GPU Setup

### CUDA Installation

For GPU acceleration, you need CUDA installed:

1. Check if CUDA is available:
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

2. If CUDA is not available, install PyTorch with CUDA support:

```bash
# For CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

3. Verify GPU detection:
```bash
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

### Multi-GPU Setup

The system automatically detects and uses multiple GPUs. No additional configuration needed.

## Redis Setup

### Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:latest
```

### Verify Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Configure Redis for Dr. Drafts

```bash
# Test connection from Python
python -c "import redis; r = redis.from_url('redis://localhost:6379'); print('Connected!' if r.ping() else 'Failed')"
```

## CouchDB Setup (Optional)

### Install CouchDB

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install couchdb
```

**macOS:**
```bash
brew install couchdb
brew services start couchdb
```

**Docker:**
```bash
docker run -d -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password couchdb:latest
```

### Install Python CouchDB Client

```bash
pip install couchdb
```

### Verify CouchDB Connection

```bash
curl http://localhost:5984/
# Should return JSON with CouchDB version

# Test from Python
python -c "import couchdb; s = couchdb.Server('http://localhost:5984'); print('Connected!')"
```

## Post-Installation Steps

### 1. Build Initial Index

```bash
# Create directories
mkdir -p index raw

# Build index with Redis
dr-drafts-build-index \
  --idir ./index \
  --rdir ./raw \
  --redis-url redis://localhost:6379 \
  --embedding-name myco:embeddings:v1
```

### 2. Test Search

```bash
dr-drafts \
  -p "machine learning for text analysis" \
  -k 5 \
  --redis-url redis://localhost:6379 \
  --embedding-name myco:embeddings:v1
```

## Troubleshooting

### Common Issues

#### Issue: "Command 'dr-drafts' not found"

**Solution:**
```bash
# Reinstall in editable mode
pip install -e .

# Or use full path
python -m dr_drafts_mycosearch.cli --help
```

#### Issue: "CUDA out of memory"

**Solution:**
Reduce batch size in [src/compute_embeddings.py](src/compute_embeddings.py):
```python
# Change batch_size from 64 to 32 or 16
embs = transformer.encode(N, batch_size=16, ...)
```

#### Issue: "Redis connection refused"

**Solution:**
```bash
# Start Redis server
sudo systemctl start redis-server  # Linux
brew services start redis          # macOS

# Or check if Redis is running
redis-cli ping
```

#### Issue: "ImportError: No module named 'couchdb'"

**Solution:**
```bash
pip install couchdb
# Or reinstall with CouchDB support
pip install -e .[couchdb]
```

#### Issue: "Torch not compiled with CUDA enabled"

**Solution:**
```bash
# Uninstall CPU-only PyTorch
pip uninstall torch

# Install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Getting Help

If you encounter issues not covered here:

1. Check the [main README](README.md)
2. Search [GitHub Issues](https://github.com/autonlab/dr-drafts-sota-literature-search/issues)
3. Create a new issue with:
   - Your Python version (`python --version`)
   - Your OS
   - Complete error message
   - Steps to reproduce

## Next Steps

- Read the [README](README.md) for usage examples
- Check [COUCHDB_INTEGRATION.md](COUCHDB_INTEGRATION.md) for CouchDB integration
- Explore [src/JUPYTER_USAGE.md](src/JUPYTER_USAGE.md) for Jupyter notebook usage
- See example scripts in the `prompts/` directory

## Uninstallation

To remove the package:

```bash
pip uninstall dr-drafts-mycosearch
```

To remove Redis (if installed):
```bash
sudo apt-get remove redis-server  # Linux
brew uninstall redis              # macOS
```

To remove CouchDB (if installed):
```bash
sudo apt-get remove couchdb  # Linux
brew uninstall couchdb       # macOS
```
