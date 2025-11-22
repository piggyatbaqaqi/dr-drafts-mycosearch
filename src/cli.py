#!/usr/bin/env python
"""
Command-line interface for Dr. Draft's Mycosearch

This module provides the main CLI entry point for the package.
"""
import sys
import os
import faulthandler
from argparse import ArgumentParser
from warnings import filterwarnings

# Add parent directory to path for SKOL imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../skol'))

from . import sota_search


def create_parser():
    """Create and configure the argument parser."""
    parser = ArgumentParser(
        prog='dr-drafts',
        description="Dr. Draft's SOTA Literature Search - Semantic search for scientific papers and grants"
    )

    parser.add_argument(
        '-p', '--prompt',
        default='CLI',
        help='Description of the work you want to do'
    )

    parser.add_argument(
        '-k', '--k',
        default=3,
        type=int,
        help='Number of top matches to return (default: 3)'
    )

    parser.add_argument(
        '-o', '--output',
        help='CSV file to store output'
    )

    parser.add_argument(
        '-t', '--title',
        default='CLI prompt',
        help='Title for results if multiple queries'
    )

    # Redis configuration
    parser.add_argument(
        '--redis-url',
        default='redis://localhost:6379',
        help='Redis URL for reading embeddings (default: redis://localhost:6379)'
    )

    parser.add_argument(
        '--redis-username',
        default=None,
        help='Redis username for authentication'
    )

    parser.add_argument(
        '--redis-password',
        default=None,
        help='Redis password for authentication'
    )

    parser.add_argument(
        '--redis-db',
        type=int,
        default=0,
        help='Redis database number (default: 0)'
    )

    parser.add_argument(
        '--embedding-name',
        default='skol:embeddings:v0.1',
        help='Name of embedding in Redis (default: skol:embeddings:v0.1)'
    )

    # Legacy support for local pickle files
    parser.add_argument(
        '--embeddings-file',
        default=None,
        help='Path to local embeddings pickle file (alternative to Redis)'
    )

    return parser


def main():
    """Main entry point for the CLI."""
    faulthandler.enable()
    filterwarnings('ignore')

    parser = create_parser()
    args = parser.parse_args()

    # Show configuration
    sota_search.show_flags(args.k, args.prompt, args.output, args.title)

    # Determine embeddings source
    if args.embeddings_file:
        # Use local pickle file
        experiment = sota_search.Experiment(
            args.prompt,
            embeddingsFN=args.embeddings_file,
            k=args.k
        )
    elif args.embedding_name:
        # Use Redis (default)
        experiment = sota_search.Experiment(
            args.prompt,
            embeddingsFN=None,
            k=args.k,
            redis_url=args.redis_url,
            redis_username=args.redis_username,
            redis_password=args.redis_password,
            redis_db=args.redis_db,
            embedding_name=args.embedding_name
        )
    else:
        # Fallback to default local file
        embeddings_file = './index/embeddings.pkl'
        if not os.path.exists(embeddings_file):
            print(f"Error: No embeddings found. Please either:")
            print(f"  1. Run 'dr-drafts-build-index' to create local embeddings")
            print(f"  2. Specify --redis-url and --embedding-name for Redis storage")
            print(f"  3. Specify --embeddings-file for a custom pickle file")
            sys.exit(1)

        experiment = sota_search.Experiment(args.prompt, embeddings_file, args.k)

    # Run the search
    experiment.run()
    results = experiment.select_results(range(args.k))

    # Expand results if we didn't get enough
    if len(results) < args.k:
        results = experiment.select_results(range(10 * args.k))

    # Remove duplicates
    results.drop_duplicates(
        subset=['Title'],
        keep='first',
        inplace=True,
        ignore_index=True
    )

    # Output results
    if not args.output:
        sota_search.results2console(results.iloc[:args.k])
    else:
        sota_search.results2csv(
            results.iloc[:args.k],
            args.output,
            args.prompt,
            args.title
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
