import json
import os
from typing import List

import pandas as pd

from ..core.common.config import OPENAI_API_KEY
from ..core.llm.openapi_client import OpenAPIClient

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))


openai_client = OpenAPIClient(api_key=OPENAI_API_KEY)


def read_data() -> pd.DataFrame:
    data_file = os.path.join(script_dir, "source_data.json")
    data_source = pd.read_json(data_file)
    return data_source


def get_openai_embeddings(docs_batch: List[dict]):
    """
    Generate embeddings for a batch of documents using OpenAI's embedding API.

    This function processes a batch of documents, extracts their text content and IDs,
    sends them to OpenAI's API for embedding generation, and returns a dictionary
    mapping document IDs to their corresponding embedding vectors.

    Args:
        docs_batch (List[dict]): A list of dictionaries, where each dictionary contains:
            - "text" (str): The text content to be embedded
            - "item_id" (str): Unique identifier for the document

    Returns:
        dict: A dictionary where:
            - Keys are document IDs (str)
            - Values are embedding vectors (list of floats)

    Example:
        >>> docs_batch = [
        ...     {"item_id": "doc1", "text": "The quick brown fox jumps"},
        ...     {"item_id": "doc2", "text": "over the lazy dog"}
        ... ]
        >>> embeddings = get_openai_embeddings(docs_batch)
        >>> print(embeddings)
        {
            'doc1': [0.1, 0.2, 0.3, ...],  # 1536-dimensional vector
            'doc2': [0.4, 0.5, 0.6, ...]   # 1536-dimensional vector
        }

    Note:
        - The embedding vectors are 1536-dimensional (OpenAI's default)
        - Each vector is normalized to have a magnitude of 1
        - The function processes documents in batches for efficiency
    """
    # Initialize lists to store texts and their corresponding IDs
    texts = []
    ids = []

    # Extract text content and IDs from each document
    for doc in docs_batch:
        texts.append(doc["text"])
        ids.append(doc["item_id"])

    # Get embeddings for all texts in a single API call
    embeddings = openai_client.get_embeddings(texts)

    # Create a dictionary mapping document IDs to their embeddings
    results = {}
    for i, doc in enumerate(docs_batch):
        results[ids[i]] = embeddings[i]

    return results


def generate_embeddings(data: pd.DataFrame) -> dict:
    """
    Generates embeddings for all items in the input DataFrame.

    Process:
    1. Processes data in batches of 100 items to avoid API rate limits
    2. For each batch:
       - Collects items into a batch
       - Calls OpenAI API to get embeddings
       - Updates the master dictionary of all embeddings
    3. Handles any remaining items after the last complete batch

    Args:
        data (pd.DataFrame): Input data containing items to be embedded

    Returns:
        dict: Dictionary mapping item IDs to their vector embeddings
    """
    all_vectors = {}  # Master dictionary to store all embeddings
    text_batch = []  # Temporary list to hold current batch of items
    item_ids = []  # List to track item IDs in current batch

    # Process data in batches of 100 items
    for index, row in data.iterrows():
        text_batch.append(row)  # Add the current item to the batch
        if index % 100 == 0:  # Process batch when we reach 100 items
            text_vectors = get_openai_embeddings(
                text_batch
            )  # Get embeddings for the current batch
            all_vectors.update(
                text_vectors
            )  # Update the master dictionary with the new embeddings
            text_batch.clear()  # Clear batch after processing
            item_ids.clear()  # Clear item IDs after processing

    # Process any remaining items that didn't make a complete batch
    if len(text_batch) > 0:
        text_vectors = get_openai_embeddings(text_batch)
        all_vectors.update(text_vectors)

    print("Length of all_vectors: ", len(all_vectors))
    print("Length of data: ", len(data))
    return all_vectors


def save_embeddings_to_json(doc_data: pd.DataFrame, embeddings: dict):
    """
    Save document embeddings to a JSON file along with their corresponding item IDs.

    This function takes the original document data and their embeddings, combines them,
    and saves them to a JSON file in a structured format. The output JSON will contain
    an array of objects, each with an item_id and its corresponding embedding vector.

    Args:
        doc_data (pd.DataFrame): DataFrame containing the original documents with columns:
            - item_id: Unique identifier for each document
        embeddings (dict): Dictionary mapping item_ids to their embedding vectors

    Example:
        >>> doc_data = pd.DataFrame({
        ...     "item_id": ["doc1", "doc2"],
        ...     "text": ["sample text 1", "sample text 2"]
        ... })
        >>> embeddings = {
        ...     "doc1": [0.1, 0.2, 0.3, ...],  # 1536-dimensional vector
        ...     "doc2": [0.4, 0.5, 0.6, ...]   # 1536-dimensional vector
        ... }
        >>> save_embeddings_to_json(doc_data, embeddings)
        # Creates embeddings.json with content:
        # [
        #     {
        #         "item_id": "doc1",
        #         "embedding": [0.1, 0.2, 0.3, ...]
        #     },
        #     {
        #         "item_id": "doc2",
        #         "embedding": [0.4, 0.5, 0.6, ...]
        #     }
        # ]
    """
    # Initialize list to store combined document and embedding data
    data_embeddings = []

    # Combine document IDs with their corresponding embeddings
    for index, row in doc_data.iterrows():
        data_embeddings.append(
            {"item_id": row["item_id"], "embedding": embeddings[row["item_id"]]}
        )

    # Convert the data to a formatted JSON string with indentation
    data_json = json.dumps(data_embeddings, indent=4)

    # Define the output directory path
    folder_path = "src\RagFlow\server\src\data"
    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Write the JSON data to file
    with open(os.path.join(folder_path, "embeddings.json"), "w") as f:
        f.write(data_json)
    print(f"Embeddings saved to {folder_path}/embeddings.json")


def save_metadata_to_json(data):
    """
    Save document metadata to a JSON file in a structured format.

    This function takes a DataFrame containing document data and extracts relevant metadata
    fields (title, text, application, article_type) along with their item_ids. The metadata
    is saved to a JSON file in a structured format that can be easily used for document
    retrieval and display.

    Args:
        data (pd.DataFrame): DataFrame containing document data with columns:
            - item_id: Unique identifier for each document
            - title: Document title
            - text: Document content
            - application: Application name/type
            - article_type: Type of article/document

    Example:
        >>> data = pd.DataFrame({
        ...     "item_id": ["doc1", "doc2"],
        ...     "title": ["Sample Title 1", "Sample Title 2"],
        ...     "text": ["Content 1", "Content 2"],
        ...     "application": ["App1", "App2"],
        ...     "article_type": ["Type1", "Type2"]
        ... })
        >>> save_metadata_to_json(data)
        # Creates metadata.json with content:
        # [
        #     {
        #         "item_id": "doc1",
        #         "metadata": {
        #             "title": "Sample Title 1",
        #             "text": "Content 1",
        #             "app": "App1",
        #             "article_type": "Type1"
        #         }
        #     },
        #     {
        #         "item_id": "doc2",
        #         "metadata": {
        #             "title": "Sample Title 2",
        #             "text": "Content 2",
        #             "app": "App2",
        #             "article_type": "Type2"
        #         }
        #     }
        # ]
    """
    # Initialize list to store metadata for each document
    metadata_list = []

    # Extract and structure metadata for each document
    for index, row in data.iterrows():
        metadata_list.append(
            {
                "item_id": row["item_id"],
                "metadata": {
                    "title": row["title"],
                    "text": row["text"],
                    "app": row["application"],
                    "article_type": row["article_type"],
                },
            }
        )

    # Convert the metadata to a formatted JSON string with indentation
    metadata_json = json.dumps(metadata_list, indent=4)

    # Define the output directory path
    folder_path = "src\RagFlow\server\src\data"
    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Write the JSON data to file
    with open(os.path.join(folder_path, "metadata.json"), "w") as f:
        f.write(metadata_json)
    print(f"Metadata saved to {folder_path}/metadata.json")


def prepare_data():
    data = read_data()
    # print("Data: ", data.head())
    embeddings = generate_embeddings(data)
    # Print both the number of embeddings and their dimension size
    if embeddings:
        first_embedding = next(
            iter(embeddings.values())
        )  # Get the first embedding only
        print(f"Number of embeddings: {len(embeddings)}")
        print(
            f"Embedding dimension size: {len(first_embedding)}"
        )  # 1536 is the dimension size of the embedding
    save_embeddings_to_json(data, embeddings)
    save_metadata_to_json(data)


if __name__ == "__main__":
    prepare_data()
