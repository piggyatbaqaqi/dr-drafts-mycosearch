"""
Dr. Draft's Mycosearch - State-of-the-art Literature Search

A semantic search system for scientific papers, grants, and taxonomic data
using sentence transformers and embedding-based similarity.
"""

__version__ = "0.2.0"
__author__ = "AutonLab"

# Import main classes for convenient access
try:
    from .sota_search import Experiment, results2console, results2csv
except ImportError:
    # Allow package to be imported even if dependencies are missing
    pass

try:
    from .compute_embeddings import EmbeddingsComputer
except ImportError:
    pass

try:
    from .build_index import IndexBuilder
except ImportError:
    pass

# Import data classes
try:
    from . import data
except ImportError:
    pass

__all__ = [
    "Experiment",
    "EmbeddingsComputer",
    "IndexBuilder",
    "data",
    "results2console",
    "results2csv",
]
