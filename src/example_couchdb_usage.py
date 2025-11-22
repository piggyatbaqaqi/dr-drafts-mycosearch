#!/usr/bin/env python3
"""
Example usage of the CouchDB integration for Dr. Drafts Mycosearch.

This script demonstrates how to use the SKOL_TAXA class to read taxon data
from CouchDB and make it available for embedding and search.
"""

import sys
from data import SKOL_TAXA

def main():
    """
    Example usage of the SKOL_TAXA data source.

    The SKOL_TAXA class reads full taxon records from a CouchDB database
    that was populated by ../skol/extract_taxa_to_couchdb.py.
    """

    # Configuration
    couchdb_url = "http://localhost:5984"
    db_name = "mycobank_taxa"  # Name of the database containing taxa

    # Optional authentication
    username = None  # Set to your CouchDB username if needed
    password = None  # Set to your CouchDB password if needed

    try:
        # Create SKOL_TAXA data source
        print(f"Connecting to CouchDB at {couchdb_url}...")
        couchdb_source = SKOL_TAXA(
            couchdb_url=couchdb_url,
            db_name=db_name,
            desc_att='description',  # Field to use for embeddings
            username=username,
            password=password
        )

        # Get descriptions for embedding
        descriptions = couchdb_source.get_descriptions()
        print(f"\nLoaded {len(descriptions)} descriptions from CouchDB")
        print(f"\nFirst few descriptions:")
        print(descriptions.head())

        # Example: Convert a specific record to display format
        if len(couchdb_source.df) > 0:
            print("\n" + "="*80)
            print("Example taxon record (converted to display format):")
            print("="*80)
            example_dict = couchdb_source.to_dict(idx=0, similarity=0.95)
            for key, value in example_dict.items():
                if value:  # Only show non-empty fields
                    print(f"{key}: {value}")

        return 0

    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo use the CouchDB integration, install the couchdb package:")
        print("  pip install couchdb")
        return 1

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
