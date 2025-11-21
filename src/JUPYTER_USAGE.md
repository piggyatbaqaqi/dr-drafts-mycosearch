# Dr. Draft's Mycosearch - Jupyter Usage Guide

This guide shows how to use the Dr. Draft's Mycosearch components in Jupyter notebooks for interactive data analysis and experimentation.

## Table of Contents
1. [EmbeddingsComputer - Computing Embeddings](#embeddingscomputer)
2. [IndexBuilder - Building Full Index](#indexbuilder)
3. [Experiment - Running Searches](#experiment)
4. [Complete Workflow Examples](#complete-workflow)

---

## EmbeddingsComputer

The `EmbeddingsComputer` class computes embeddings from narrative data and stores them locally or in Redis.

### Import

```python
from src.compute_embeddings import EmbeddingsComputer
```

### Example 1: Write to local file (default)

```python
computer = EmbeddingsComputer(idir='./index')
result = computer.run()

# Access the results
print(result.head())
print(f"Shape: {result.shape}")
print(f"Columns: {result.columns.tolist()}")
```

### Example 2: Write to custom pickle file

```python
computer = EmbeddingsComputer(
    idir='./index',
    pickle_file='./custom_embeddings.pkl'
)
result = computer.run()
```

### Example 3: Write to Redis

```python
computer = EmbeddingsComputer(
    idir='./index',
    redis_url='redis://localhost:6379',
    embedding_name='my_embeddings'
)
result = computer.run()

# With authentication
computer = EmbeddingsComputer(
    idir='./index',
    redis_url='redis://localhost:6379',
    redis_username='myuser',
    redis_password='mypassword',
    embedding_name='my_embeddings'
)
result = computer.run()
```

### Example 4: Use custom embedding model

```python
computer = EmbeddingsComputer(
    idir='./index',
    model_name='sentence-transformers/all-MiniLM-L6-v2'  # Smaller, faster model
)
result = computer.run()
```

### Example 5: Access intermediate steps

```python
computer = EmbeddingsComputer(idir='./index')

# Just load data objects
objects = computer.glob2objects('./index/*_S*')
print(f"Found {len(objects)} data files")

# Convert to descriptions
descriptions = computer.objects2descriptions(objects)
print(f"Extracted {len(descriptions)} descriptions")

# Compute embeddings for a subset
sample_descriptions = descriptions.head(100)
embeddings = computer.encode_narratives(sample_descriptions['description'].astype(str))
print(f"Embedding shape: {embeddings.shape}")
```

---

## IndexBuilder

The `IndexBuilder` class orchestrates the full pipeline: data preparation scripts + embeddings computation.

### Import

```python
from src.build_index import IndexBuilder
```

### Example 1: Build complete index (local file)

```python
builder = IndexBuilder(idir='./index')
embeddings = builder.run()

print(f"Built index with {len(embeddings)} embeddings")
```

### Example 2: Build index with custom directories

```python
builder = IndexBuilder(
    idir='./my_index',
    rdir='./my_raw_data',
    sdir='./src',
    maxlines=5000  # Smaller chunks
)
embeddings = builder.run()
```

### Example 3: Build index to Redis

```python
builder = IndexBuilder(
    idir='./index',
    redis_url='redis://localhost:6379',
    embedding_name='production_embeddings'
)
embeddings = builder.run()
```

### Example 4: Run individual steps

```python
builder = IndexBuilder(idir='./index')

# Step 1: Create directories
builder.create_directories()

# Step 2: Run data preparation scripts
results = builder.run_data_prep_scripts()
for script, return_code in results:
    status = "✓" if return_code == 0 else "✗"
    print(f"{status} {script}: exit code {return_code}")

# Step 3: Compute embeddings
embeddings = builder.compute_embeddings()
print(f"Computed {len(embeddings)} embeddings")
```

### Example 5: Build multiple indexes

```python
# Build separate indexes for different datasets
configs = [
    {'idir': './index_v1', 'embedding_name': 'embeddings_v1'},
    {'idir': './index_v2', 'embedding_name': 'embeddings_v2'},
]

results = {}
for config in configs:
    builder = IndexBuilder(
        redis_url='redis://localhost:6379',
        **config
    )
    results[config['embedding_name']] = builder.run()

print(f"Built {len(results)} indexes")
```

---

## Experiment

The `Experiment` class performs similarity searches using pre-computed embeddings.

### Import

```python
from src.sota_search import Experiment
```

### Example 1: Search with local embeddings file

```python
experiment = Experiment(
    prompt='machine learning for climate change prediction',
    embeddingsFN='./index/embeddings.pkl',
    k=10
)
experiment.run()

# Get top results
results = experiment.select_results(range(10))
print(results[['Title', 'Similarity']])
```

### Example 2: Search with Redis embeddings

```python
experiment = Experiment(
    prompt='natural language processing for medical diagnosis',
    embeddingsFN=None,
    k=20,
    redis_url='redis://localhost:6379',
    embedding_name='my_embeddings'
)
experiment.run()

results = experiment.select_results(range(20))
print(f"Found {len(results)} results")
```

### Example 3: Multiple searches on same embeddings

```python
# Load embeddings once
experiment = Experiment(
    prompt='',  # Will change this
    embeddingsFN='./index/embeddings.pkl',
    k=5
)

# Run multiple searches
queries = [
    'computer vision applications',
    'quantum computing algorithms',
    'sustainable energy systems'
]

all_results = {}
for query in queries:
    experiment.prompt = query
    experiment.run()
    results = experiment.select_results(range(5))
    all_results[query] = results
    print(f"\n{query}: {len(results)} results")
```

### Example 4: Analyze similarity distributions

```python
import matplotlib.pyplot as plt

experiment = Experiment(
    prompt='artificial intelligence in healthcare',
    embeddingsFN='./index/embeddings.pkl',
    k=100
)
experiment.run()

# Get similarity scores
results = experiment.select_results(range(100))

# Plot distribution
plt.figure(figsize=(10, 6))
plt.hist(results['Similarity'], bins=20, edgecolor='black')
plt.xlabel('Cosine Similarity')
plt.ylabel('Frequency')
plt.title('Similarity Score Distribution')
plt.show()

# Show statistics
print(f"Mean similarity: {results['Similarity'].mean():.4f}")
print(f"Median similarity: {results['Similarity'].median():.4f}")
print(f"Max similarity: {results['Similarity'].max():.4f}")
```

### Example 5: Filter results by similarity threshold

```python
experiment = Experiment(
    prompt='deep learning frameworks',
    embeddingsFN='./index/embeddings.pkl',
    k=50
)
experiment.run()

results = experiment.select_results(range(50))

# Filter for high similarity only
high_quality = results[results['Similarity'] > 0.7]
print(f"Found {len(high_quality)} highly similar results")
print(high_quality[['Title', 'Similarity', 'URL']])
```

---

## Complete Workflow

### End-to-End Example: Build Index and Search

```python
from src.build_index import IndexBuilder
from src.sota_search import Experiment

# 1. Build the index
print("Building index...")
builder = IndexBuilder(idir='./index')
embeddings = builder.run()
print(f"Index built: {len(embeddings)} embeddings")

# 2. Run search
print("\nRunning search...")
experiment = Experiment(
    prompt='federated learning for privacy-preserving AI',
    embeddingsFN='./index/embeddings.pkl',
    k=10
)
experiment.run()

# 3. Get and display results
results = experiment.select_results(range(10))
print(f"\nTop {len(results)} results:")
for idx, row in results.iterrows():
    print(f"{idx+1}. [{row['Similarity']:.4f}] {row['Title']}")
    print(f"   {row['URL']}")
```

### Redis-Based Production Workflow

```python
from src.build_index import IndexBuilder
from src.sota_search import Experiment

# Configuration
REDIS_CONFIG = {
    'redis_url': 'redis://localhost:6379',
    'embedding_name': 'production_v1'
}

# 1. Build and store in Redis
print("Building index and storing in Redis...")
builder = IndexBuilder(idir='./index', **REDIS_CONFIG)
builder.run()
print("Index stored in Redis")

# 2. Search using Redis embeddings
print("\nSearching...")
experiment = Experiment(
    prompt='blockchain for supply chain management',
    embeddingsFN=None,
    k=15,
    **REDIS_CONFIG
)
experiment.run()

results = experiment.select_results(range(15))
print(f"Found {len(results)} results from Redis")

# 3. Export to CSV
results.to_csv('search_results.csv', index=False)
print("Results exported to search_results.csv")
```

### Batch Processing Multiple Queries

```python
from src.sota_search import Experiment
import pandas as pd

# Load embeddings once
embeddings_path = './index/embeddings.pkl'

# Define multiple queries
queries = {
    'ml_healthcare': 'machine learning applications in healthcare diagnostics',
    'nlp_legal': 'natural language processing for legal document analysis',
    'cv_robotics': 'computer vision for autonomous robotics',
    'rl_games': 'reinforcement learning in game AI'
}

# Run all queries
all_results = []
for query_name, query_text in queries.items():
    print(f"Processing: {query_name}")

    experiment = Experiment(
        prompt=query_text,
        embeddingsFN=embeddings_path,
        k=20
    )
    experiment.run()

    results = experiment.select_results(range(20))
    results['QueryName'] = query_name
    results['QueryText'] = query_text
    all_results.append(results)

# Combine all results
combined = pd.concat(all_results, ignore_index=True)
combined.to_csv('batch_results.csv', index=False)
print(f"\nTotal results: {len(combined)}")
```

### Incremental Index Updates

```python
from src.compute_embeddings import EmbeddingsComputer
import pandas as pd

# Load existing embeddings
existing = pd.read_pickle('./index/embeddings.pkl')
print(f"Existing embeddings: {len(existing)}")

# Compute new embeddings for additional data
computer = EmbeddingsComputer(
    idir='./new_data',
    pickle_file='./index/new_embeddings.pkl'
)
new_embeddings = computer.run()
print(f"New embeddings: {len(new_embeddings)}")

# Merge embeddings
combined = pd.concat([existing, new_embeddings], ignore_index=True)
combined = combined.drop_duplicates(subset=['description'], keep='last')
print(f"Combined embeddings: {len(combined)}")

# Save merged index
combined.to_pickle('./index/embeddings_merged.pkl')
print("Merged index saved")
```

---

## Notes

- The command-line interfaces remain unchanged, so all existing scripts continue to work
- Redis support is optional; local file storage works without any Redis installation
- All classes return pandas DataFrames for easy integration with data analysis workflows
- Embeddings are cached in memory within each class instance for efficiency
