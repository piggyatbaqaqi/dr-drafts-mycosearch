"""
Build index for Dr. Draft's Proposal Test-O-Meter.

This module handles data preparation and embeddings computation.
Can write embeddings to local filesystem or Redis.
"""
import os
import subprocess
from glob import glob
from typing import Optional
from argparse import ArgumentParser
from compute_embeddings import EmbeddingsComputer


class IndexBuilder:
    """Class for building the embeddings index from raw data."""

    def __init__(self,
                 idir: str = './index',
                 rdir: str = './raw',
                 sdir: str = './src',
                 maxlines: int = 10000,
                 pickle_file: Optional[str] = None,
                 redis_url: Optional[str] = None,
                 redis_username: Optional[str] = None,
                 redis_password: Optional[str] = None,
                 redis_db: int = 0,
                 embedding_name: Optional[str] = None):
        """Initialize the IndexBuilder.

        Args:
            idir (str): Index directory for processed data
            rdir (str): Raw data directory
            sdir (str): Source directory containing scripts
            maxlines (int): Maximum lines per split file
            pickle_file (str, optional): Custom pickle file path
            redis_url (str, optional): Redis URL
            redis_username (str, optional): Redis username
            redis_password (str, optional): Redis password
            redis_db (int): Redis database number (default: 0)
            embedding_name (str, optional): Name for embedding in Redis
        """
        self.idir = idir
        self.rdir = rdir
        self.sdir = sdir
        self.maxlines = maxlines
        self.pickle_file = pickle_file
        self.redis_url = redis_url
        self.redis_username = redis_username
        self.redis_password = redis_password
        self.redis_db = redis_db
        self.embedding_name = embedding_name
        self.result = None

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.idir, exist_ok=True)
        os.makedirs(self.rdir, exist_ok=True)
        print(f"Created directories: {self.idir}, {self.rdir}")

    def run_data_prep_scripts(self):
        """Run all get_*.sh scripts for data preparation.

        Returns:
            list: List of (script_path, return_code) tuples
        """
        pattern = os.path.join(self.sdir, 'get_*')
        scripts = glob(pattern)

        if not scripts:
            print(f"Warning: No data preparation scripts found matching {pattern}")
            return []

        results = []
        for script in scripts:
            print(f"Running: {script}")
            try:
                result = subprocess.run(
                    [script, self.idir, self.rdir, self.sdir, str(self.maxlines)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
                results.append((script, 0))
            except subprocess.CalledProcessError as e:
                print(f"Error running {script}: {e}")
                print(f"Stdout: {e.stdout}")
                print(f"Stderr: {e.stderr}")
                results.append((script, e.returncode))
            except Exception as e:
                print(f"Unexpected error running {script}: {e}")
                results.append((script, -1))

        return results

    def compute_embeddings(self):
        """Compute embeddings using EmbeddingsComputer.

        Returns:
            pandas.DataFrame: The computed embeddings
        """
        print('Building index for Dr. Drafts Proposal Test-O-Meter')

        computer = EmbeddingsComputer(
            idir=self.idir,
            pickle_file=self.pickle_file,
            redis_url=self.redis_url,
            redis_username=self.redis_username,
            redis_password=self.redis_password,
            redis_db=self.redis_db,
            embedding_name=self.embedding_name
        )

        self.result = computer.run()
        return self.result

    def run(self):
        """Run the full index building pipeline.

        Returns:
            pandas.DataFrame: The computed embeddings
        """
        self.create_directories()
        self.run_data_prep_scripts()
        return self.compute_embeddings()


if __name__ == "__main__":
    parser = ArgumentParser(
        description='Build index for Dr. Drafts Proposal Test-O-Meter'
    )
    parser.add_argument('--idir', default='./index',
                       help='Index directory (default: ./index)')
    parser.add_argument('--rdir', default='./raw',
                       help='Raw data directory (default: ./raw)')
    parser.add_argument('--sdir', default='./src',
                       help='Source directory (default: ./src)')
    parser.add_argument('--maxlines', type=int, default=10000,
                       help='Maximum lines per split file (default: 10000)')
    parser.add_argument('--pickle-file', default=None,
                       help='Path to output pickle file (default: IDIR/embeddings.pkl)')
    parser.add_argument('--redis-url', default='redis://localhost:6379',
                       help='Redis URL for storing embeddings')
    parser.add_argument('--redis-username', default=None,
                       help='Redis username')
    parser.add_argument('--redis-password', default=None,
                       help='Redis password')
    parser.add_argument('--redis-db', type=int, default=0,
                       help='Redis database number (default: 0)')
    parser.add_argument('--embedding-name', default=None,
                       help='Name for embedding in Redis')
    args = parser.parse_args()

    # Create IndexBuilder and run
    builder = IndexBuilder(
        idir=args.idir,
        rdir=args.rdir,
        sdir=args.sdir,
        maxlines=args.maxlines,
        pickle_file=args.pickle_file,
        redis_url=args.redis_url,
        redis_username=args.redis_username,
        redis_password=args.redis_password,
        redis_db=args.redis_db,
        embedding_name=args.embedding_name
    )
    builder.run()
