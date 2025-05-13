import json
import os
import numpy as np
import redis
from redis.commands.search.field import (
    VectorField,
    TagField,
)
from redis.commands.search.index_definition import IndexDefinition, IndexType

from .prepare_data import read_data

# from ..core.common.config import REDIS_URL

REDIS_URL = os.getenv("REDIS_URL")

redis_conn = redis.from_url(REDIS_URL)
print(redis_conn.ping())

def persist_data(embeddings_data: list, metadata_data: list):
    pass


def read_embeddings_data():
    folder_path = "src\RagFlow\server\src\data"
    with open(os.path.join(folder_path, "embeddings.json"), "r") as f:
        embeddings_data = json.load(f)
    return embeddings_data



def read_metadata_data():
    folder_path = "src\RagFlow\server\src\data"
    with open(os.path.join(folder_path, "metadata.json"), "r") as f:
        metadata_data = json.load(f)
    return metadata_data

def create_index(embeddings_data, metadata_data):
    pass

def load_data():
    # we want to load data only if the database is empty
    if redis_conn.dbsize() > 5000:
        print("Database is not empty. Data is already loaded.")
        return None
    embeddings_data = read_embeddings_data()
    metadata_data = read_metadata_data()
    persist_data(embeddings_data, metadata_data)
    create_index(embeddings_data, metadata_data)

if __name__ == "__main__":
    persist_data()
    load_data()

