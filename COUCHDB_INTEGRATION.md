# CouchDB Integration for Dr. Drafts Mycosearch

This document describes the CouchDB integration that allows reading taxon data directly from CouchDB for embedding and search.

## Overview

The `COUCHDB` class in [src/data.py](src/data.py) provides integration with CouchDB databases containing taxon records created by the `../skol/extract_taxa_to_couchdb.py` pipeline. This integration makes full taxon records from CouchDB accessible to the Dr. Drafts search system.

## Installation

To use the CouchDB integration, you need to install the `couchdb` Python package:

```bash
pip install couchdb
```

## Usage

### Basic Usage

```python
from data import COUCHDB

# Create a COUCHDB data source
couchdb_source = COUCHDB(
    couchdb_url="http://localhost:5984",
    db_name="mycobank_taxa",
    desc_att='description'  # Field to use for embeddings
)

# Get descriptions for embedding
descriptions = couchdb_source.get_descriptions()
print(f"Loaded {len(descriptions)} records")

# Convert a specific record to display format
result = couchdb_source.to_dict(idx=0, similarity=0.95)
```

### With Authentication

```python
from data import COUCHDB

# Connect with username and password
couchdb_source = COUCHDB(
    couchdb_url="http://localhost:5984",
    db_name="mycobank_taxa",
    desc_att='description',
    username="admin",
    password="secret"
)
```

### Using with Embeddings

The COUCHDB data source works seamlessly with the existing embeddings pipeline:

```python
from compute_embeddings import EmbeddingsComputer
from data import COUCHDB

# Load data from CouchDB
couchdb_source = COUCHDB(
    couchdb_url="http://localhost:5984",
    db_name="mycobank_taxa"
)

# Get descriptions and compute embeddings
descriptions = couchdb_source.get_descriptions()
# ... continue with embedding computation
```

## Data Structure

The `COUCHDB` class expects documents in the format created by `extract_taxa_to_couchdb.py`:

```json
{
  "_id": "taxon_abc123...",
  "_rev": "1-xyz...",
  "taxon": "Nomenclature text",
  "description": "Description text",
  "source": {
    "doc_id": "source_document_id",
    "url": "http://example.com/source",
    "db_name": "mycobank_annotations"
  },
  "line_number": "123",
  "paragraph_number": "45",
  "page_number": "67",
  "empirical_page_number": "2"
}
```

## Key Features

1. **Direct Database Access**: Reads full taxon records directly from CouchDB without intermediate CSV files
2. **Full Record Access**: Preserves all metadata from the original taxon extraction
3. **Standard Interface**: Implements the same `Raw_Data_Index` interface as other data sources
4. **Flexible Authentication**: Supports both anonymous and authenticated CouchDB access
5. **Integration with Embeddings**: Works with the existing `compute_embeddings.py` pipeline

## Methods

### `__init__(couchdb_url, db_name, desc_att='description', username=None, password=None)`

Creates a new COUCHDB data source.

**Parameters:**
- `couchdb_url` (str): URL of the CouchDB server (e.g., 'http://localhost:5984')
- `db_name` (str): Name of the CouchDB database containing taxa
- `desc_att` (str): Description attribute to use for embeddings (default: 'description')
- `username` (str, optional): CouchDB username for authentication
- `password` (str, optional): CouchDB password for authentication

### `load_data()`

Loads all taxon documents from CouchDB into a pandas DataFrame. Automatically skips design documents.

### `get_descriptions()`

Returns a DataFrame with source information and descriptions for embedding:
- `source`: Class name ('COUCHDB')
- `filename`: Database identifier
- `row`: DataFrame index
- `description`: Text to embed

### `to_dict(idx, similarity)`

Converts a taxon record to the standard result dictionary format for display.

**Parameters:**
- `idx` (int): Row index in the DataFrame
- `similarity` (float): Similarity score from embedding comparison

**Returns:**
- Dictionary with standardized keys matching other data sources

## Example Script

See [src/example_couchdb_usage.py](src/example_couchdb_usage.py) for a complete working example:

```bash
cd src
python example_couchdb_usage.py
```

## Integration with Build Pipeline

To use CouchDB data in the build pipeline, you can save CouchDB records to pickle files that follow the naming convention expected by `compute_embeddings.py`:

```python
from data import COUCHDB
import pickle

# Load from CouchDB
couchdb_source = COUCHDB(
    couchdb_url="http://localhost:5984",
    db_name="mycobank_taxa"
)

# Save to pickle file for use with compute_embeddings.py
# The filename must match pattern: CLASSNAME_S*.pkl
with open('./index/COUCHDB_S0001.pkl', 'wb') as f:
    pickle.dump(couchdb_source.df, f)
```

Then the standard `compute_embeddings.py` pipeline will automatically include CouchDB data:

```bash
python compute_embeddings.py ./index \
  --redis-url redis://localhost:6379 \
  --embedding-name mycobank_embeddings
```

## Relationship to extract_taxa_to_couchdb.py

This integration reads data created by the `../skol/extract_taxa_to_couchdb.py` script, which:

1. Reads annotated files from a CouchDB ingest database
2. Extracts Taxon objects using the SKOL pipeline
3. Saves Taxa as JSON documents to a taxon CouchDB database
4. Uses deterministic document IDs based on (doc_id, url, line_number) for idempotent writes

The `COUCHDB` class provides the read-side of this pipeline, making the extracted taxa available for search and discovery.

## Troubleshooting

### ImportError: couchdb package required

Install the couchdb package:
```bash
pip install couchdb
```

### Database not found

Ensure the database exists in CouchDB:
```bash
curl http://localhost:5984/_all_dbs
```

### Authentication errors

Check your username and password, and ensure the user has read access to the database.

### No records found

The database may be empty or contain only design documents. Check using:
```bash
curl http://localhost:5984/mycobank_taxa/_all_docs
```
