## Usage in Jupyter

You can now import and use the class in Jupyter notebooks:
from src.compute_embeddings import EmbeddingsComputer

### Example 1: Write to local file

```python
computer = EmbeddingsComputer(idir='./index')
result = computer.run()
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
```

### Access the results

```python
print(result.head())
print(f"Shape: {result.shape}")
```

The command-line interface remains unchanged, so all your existing scripts will continue to work!
