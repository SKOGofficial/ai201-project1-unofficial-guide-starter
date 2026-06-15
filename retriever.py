import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in the vector database.
    Each chunk is a dict with: "text", "metadata", "chunk_id"
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant hardware guide chunks for a user's question.
    """
    if _collection.count() == 0:
        return []

    info = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i in range(len(info["documents"][0])):
        meta = info["metadatas"][0][i]
        chunks.append(
            {
                "text": info["documents"][0][i],
                "source": meta.get("source", "Unknown"),
                "file": meta.get("file", "Unknown"),
                "line": meta.get("line", 0),
                "distance": info["distances"][0][i],
                "metadata": meta # Keep all metadata just in case
            }
        )

    return chunks
