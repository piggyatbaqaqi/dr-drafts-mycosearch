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
from typing import List, Optional
from glob import glob
from sentence_transformers import SentenceTransformer
import pandas
import torch
import data as DATA_CLASSES
import pickle
from argparse import ArgumentParser

MODEL_NAME = 'all-mpnet-base-v2'
DESCRIPTION_ATTR = {
                    'SKOL': 'description'
                    }


def encode_narratives(N: List[str]) -> pandas.DataFrame:
    """Encode narratives using SentenceTransformer. Multi-GPU support.

    Model is set to all-mpnet-base-v2.

    Args:
        N (List[str]): List of narratives to encode. Descriptions of CFPs/FOAs.

    Returns:
        pandas.DataFrame: DataFrame with #narratives x #dims.
    """
    transformer = SentenceTransformer(MODEL_NAME)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.device_count() > 1:
        tds = ['cuda:1', 'cuda:2', 'cuda:0', 'cuda:3']
        pool = transformer.start_multi_process_pool(target_devices=tds)
        embs = transformer.encode_multi_process(N,
                                                pool,
                                                batch_size=1024,  # 128
                                                chunk_size=len(N)/1000  # 100
                                                )
        transformer.stop_multi_process_pool(pool)
    else:
        embs = transformer.encode(N,
                                  show_progress_bar=True,
                                  batch_size=64,
                                  device=device
                                  )
    ncols = len(embs[0])
    attnames = [f'F{i}' for i in range(ncols)]
    return pandas.DataFrame(embs, columns=attnames)


def glob2objects(glob_pattern: str):
    """Convert globbed files to objects.

    Args:
        glob_pattern (str): Which files to include

    Returns:
        List[obj]: A list of class objects for reading each raw data files
    """
    files = list(glob(glob_pattern))
    classes = [f.split('/')[-1].split('_')[0] for f in files]
    zset = zip(files, classes)
    print('zset',zset)
    objs = [getattr(DATA_CLASSES, c)(f, DESCRIPTION_ATTR[c]) for f, c in zset]
    print('obj',objs)
    return objs


def objects2descriptions(Objs: list):
    """Convert objects to descriptions.

    Args:
        objects (list): List of class objects

    Returns:
        pandas.DataFrame: DataFrame with descriptions read from objects
    """
    return pandas.concat([obj.get_descriptions() for obj in Objs],
                         ignore_index=True)


def write_embeddings_to_redis(embeddings_df: pandas.DataFrame,
                              redis_url: str,
                              embedding_name: str,
                              redis_username: Optional[str] = None,
                              redis_password: Optional[str] = None):
    """Write embeddings to Redis.

    Args:
        embeddings_df (pandas.DataFrame): DataFrame containing embeddings
        redis_url (str): Redis URL
        embedding_name (str): Name to store the embedding under
        redis_username (str, optional): Redis username
        redis_password (str, optional): Redis password
    """
    import redis

    if redis_username and redis_password:
        r = redis.from_url(redis_url, username=redis_username, password=redis_password)
    else:
        r = redis.from_url(redis_url)

    pickled_data = pickle.dumps(embeddings_df)
    r.set(embedding_name, pickled_data)
    print(f'Embeddings written to Redis with key: {embedding_name}')


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
    parser.add_argument('--embedding-name', default=None,
                       help='Name for embedding in Redis')
    args = parser.parse_args()

    IDIR = args.idir
    objects = glob2objects(f'{IDIR}/*_S*')
    descriptions = objects2descriptions(objects)
    df = descriptions.drop_duplicates(
        subset=['description'],
        keep='last',
        ignore_index=True
        )
    #df = descriptions
    if not torch.cuda.is_available():
        print('Warning: No GPU detected. Using CPU.')
    embeddings = encode_narratives(df.description.astype(str))
    result = pandas.concat([df, embeddings], axis=1)

    # Write to Redis if embedding name is specified
    if args.embedding_name:
        if not args.redis_url:
            raise ValueError("--redis-url must be provided when --embedding-name is specified")
        write_embeddings_to_redis(
            result,
            args.redis_url,
            args.embedding_name,
            args.redis_username,
            args.redis_password
        )
    else:
        # Write to local filesystem
        output_file = args.pickle_file if args.pickle_file else f'{IDIR}/embeddings.pkl'
        result.to_pickle(output_file)
        print(f'Embeddings written to: {output_file}')
