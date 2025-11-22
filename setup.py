#!/usr/bin/env python
"""
Setup script for dr-drafts-mycosearch

This is provided for backward compatibility with older pip versions.
For modern installations, use pyproject.toml instead:
    pip install -e .
"""

from setuptools import setup

# Read version and other metadata from pyproject.toml if available
# Otherwise, fall back to hardcoded values
try:
    import tomli
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
        metadata = pyproject["project"]
except (ImportError, FileNotFoundError):
    # Fallback metadata if pyproject.toml is not available
    metadata = {
        "name": "dr-drafts-mycosearch",
        "version": "0.2.0",
        "description": "State-of-the-art literature search and embedding-based discovery",
    }

if __name__ == "__main__":
    setup()
