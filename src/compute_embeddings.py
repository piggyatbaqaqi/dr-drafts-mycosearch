"""
Compute embeddings for narratives using SentenceTransformer.

Args:
    IDIR (str): index director path to directory containing pickled CFPs/FOAs.
    data_files: Files containing CFP/FOA data. Split by get_*.sh scripts
Returns:
    index_directory/embeddings.pkl
"""
import sys
sys.path.append('../skol')
from typing import Iterable, Optional
from glob import glob
from sentence_transformers import SentenceTransformer
import pandas
import torch
import data as DATA_CLASSES
import pickle
from argparse import ArgumentParser

import redis

MODEL_NAME = 'all-mpnet-base-v2'
DESCRIPTION_ATTR = {
                    'SKOL': 'description',
                    'SKOL_TAXA': 'description'
                    }


class EmbeddingsComputer:
    """Class for computing and storing embeddings from narrative data."""

    def __init__(self, idir: str,
                 pickle_file: Optional[str] = None,
                 redis_url: Optional[str] = None,
                 redis_username: Optional[str] = None,
                 redis_password: Optional[str] = None,
                 redis_db: int = 0,
                 redis_expire: Optional[int] = None,
                 embedding_name: Optional[str] = None,
                 model_name: str = MODEL_NAME):
        """Initialize the EmbeddingsComputer.

        Args:
            idir (str): Index directory path containing pickled CFPs/FOAs
            pickle_file (str, optional): Path to output pickle file
            redis_url (str, optional): Redis URL for storing embeddings
            redis_username (str, optional): Redis username
            redis_password (str, optional): Redis password
            redis_db (int): Redis database number (default: 0)
            redis_expire (int, optional): Expiration time for Redis entries
             in seconds
            embedding_name (str, optional): Name for embedding in Redis
            model_name (str): SentenceTransformer model name
        """
        self.idir = idir
        self.pickle_file = pickle_file
        self.redis_url = redis_url
        self.redis_username = redis_username
        self.redis_password = redis_password
        self.redis_db = redis_db
        self.redist_expire = redis_expire
        self.embedding_name = embedding_name
        self.model_name = model_name
        self.result = None

    def encode_narratives(self, N: Iterable[str]) -> pandas.DataFrame:
        """Encode narratives using SentenceTransformer. Multi-GPU support.

        Model is set to all-mpnet-base-v2.

        Args:
            N (List[str]): List of narratives to encode. Descriptions of CFPs/FOAs.

        Returns:
            pandas.DataFrame: DataFrame with #narratives x #dims.
        """
        # Initialize model and move to GPU if available
        transformer = SentenceTransformer(self.model_name)

        # Determine device and report it
        if torch.cuda.is_available():
            device_str = "cuda"
            gpu_props = torch.cuda.get_device_properties(0)
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {gpu_props.total_memory / 1e9:.2f} GB")
        else:
            device_str = "cpu"
            print("Warning: No GPU detected. Using CPU.")

        # Check for multi-GPU setup
        if torch.cuda.device_count() > 1:
            print(f"Using {torch.cuda.device_count()} GPUs for multi-process encoding")
            tds = [f'cuda:{i}' for i in range(torch.cuda.device_count())]
            pool = transformer.start_multi_process_pool(target_devices=tds)
            embs = transformer.encode_multi_process(N,
                                                    pool,
                                                    batch_size=1024,  # 128
                                                    chunk_size=len(N)//1000 if len(N) > 1000 else None
                                                    )
            transformer.stop_multi_process_pool(pool)
        else:
            # Single GPU or CPU - use device parameter as string
            embs = transformer.encode(N,
                                      show_progress_bar=True,
                                      batch_size=64,
                                      device=device_str  # Pass string instead of torch.device
                                      )
        ncols = len(embs[0])
        attnames = [f'F{i}' for i in range(ncols)]
        return pandas.DataFrame(embs, columns=attnames)


    def glob2objects(self, glob_pattern: str):
        """Convert globbed files to objects.

        Args:
            glob_pattern (str): Which files to include

        Returns:
            List[obj]: A list of class objects for reading each raw data files
        """
        files = list(glob(glob_pattern))
        classes = [f.split('/')[-1].split('_')[0] for f in files]
        zset = zip(files, classes)
        print('zset', zset)
        objs = [getattr(DATA_CLASSES, c)(f, DESCRIPTION_ATTR[c]) for f, c in zset]
        print('obj', objs)
        return objs

    def objects2descriptions(self, Objs: list):
        """Convert objects to descriptions.

        Args:
            objects (list): List of class objects

        Returns:
            pandas.DataFrame: DataFrame with descriptions read from objects
        """
        return pandas.concat([obj.get_descriptions() for obj in Objs],
                             ignore_index=True)


    def write_embeddings_to_redis(self):
        """Write embeddings to Redis using instance configuration.

        Supports TLS connections via rediss:// URLs. When using TLS,
        the system CA certificates are used for verification.
        """
        kwargs = {'db': self.redis_db}

        # Add authentication if configured
        if self.redis_username:
            kwargs['username'] = self.redis_username
        if self.redis_password:
            kwargs['password'] = self.redis_password

        # Configure TLS if using rediss:// URL
        if self.redis_url and self.redis_url.startswith('rediss://'):
            kwargs['ssl_ca_certs'] = '/etc/ssl/certs/ca-certificates.crt'
            # Don't verify hostname (cert is for synoptickeyof.life but we connect to localhost)
            kwargs['ssl_check_hostname'] = False

        r = redis.from_url(self.redis_url, **kwargs)

        pickled_data = pickle.dumps(self.result)
        r.set(self.embedding_name, pickled_data)
        if self.redist_expire is not None:
            r.expire(self.embedding_name, self.redist_expire)
        print(f'Embeddings written to Redis (db={self.redis_db}) with key: {self.embedding_name}')

    def write_embeddings_to_file(self):
        """Write embeddings to local filesystem using instance configuration."""
        output_file = self.pickle_file if self.pickle_file else f'{self.idir}/embeddings.pkl'
        self.result.to_pickle(output_file)
        print(f'Embeddings written to: {output_file}')

    def run(self, df: pandas.DataFrame) -> pandas.DataFrame:
        """Run embeddings computation on a pandas DataFrame.

        Args:
            df (pandas.DataFrame): DataFrame with 'description' column

        Returns:
            pandas.DataFrame: Original data concatenated with embeddings
        """
        if not torch.cuda.is_available():
            print('Warning: No GPU detected. Using CPU.')

        embeddings = self.encode_narratives(df.description.astype(str))
        self.result = pandas.concat([df, embeddings], axis=1)
        # Write to Redis if embedding name is specified
        if self.embedding_name:
            if not self.redis_url:
                raise ValueError("redis_url must be provided when embedding_name is specified")
            self.write_embeddings_to_redis()
        else:
            # Write to local filesystem
            self.write_embeddings_to_file()

        return self.result

    def run_local(self):
        """Run embeddings computation from local filesystem.

        Returns:
            pandas.DataFrame: The computed embeddings
        """
        objects = self.glob2objects(f'{self.idir}/*_S*')
        descriptions = self.objects2descriptions(objects)
        df = descriptions.drop_duplicates(
            subset=['description'],
            keep='last',
            ignore_index=True
        )

        return self.run(df)


if __name__ == "__main__":
    parser = ArgumentParser(description='Compute embeddings for narratives')
    parser.add_argument('idir', help='Index directory path containing pickled CFPs/FOAs')
    parser.add_argument('--pickle-file', default=None,
                       help='Path to output pickle file (default: IDIR/embeddings.pkl)')
    parser.add_argument('--redis-url', default=None,
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

    # Create EmbeddingsComputer instance and run
    computer = EmbeddingsComputer(
        idir=args.idir,
        pickle_file=args.pickle_file,
        redis_url=args.redis_url,
        redis_username=args.redis_username,
        redis_password=args.redis_password,
        redis_db=args.redis_db,
        embedding_name=args.embedding_name
    )
    computer.run_local()
