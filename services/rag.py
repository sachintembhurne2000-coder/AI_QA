"""
RAG Service — ChromaDB vector store for knowledge base retrieval
"""
import hashlib
from pathlib import Path
from typing import Optional
from services.parser import chunk_text


CHROMA_DIR = ".chroma_db"


def _get_client():
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        return client
    except ImportError:
        raise ImportError("chromadb not installed. Run: pip install chromadb")


def _get_collection(client, name: str = "qa_copilot_kb"):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def add_document(text: str, source_name: str, doc_type: str = "general") -> int:
    """
    Chunk text and add to vector store.
    Returns number of chunks added.
    """
    client = _get_client()
    collection = _get_collection(client)

    chunks = chunk_text(text)
    ids, documents, metadatas = [], [], []

    for i, chunk in enumerate(chunks):
        doc_id = hashlib.md5(f"{source_name}_{i}_{chunk[:50]}".encode()).hexdigest()
        ids.append(doc_id)
        documents.append(chunk)
        metadatas.append({"source": source_name, "type": doc_type, "chunk": i})

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    return len(ids)


def query(question: str, n_results: int = 5, doc_type: Optional[str] = None) -> list[dict]:
    """
    Semantic search over knowledge base.
    Returns list of {text, source, score} dicts.
    """
    try:
        client = _get_client()
        collection = _get_collection(client)

        where = {"type": doc_type} if doc_type else None
        kwargs = {
            "query_texts": [question],
            "n_results": min(n_results, max(collection.count(), 1)),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "type": meta.get("type", "general"),
                "score": round(1 - dist, 3),   # cosine similarity
            })
        return output

    except Exception as e:
        return []


def build_context(question: str, n_results: int = 5) -> str:
    """Build a context string from top RAG results for prompt injection."""
    results = query(question, n_results)
    if not results:
        return ""
    parts = []
    for r in results:
        parts.append(f"[Source: {r['source']} | Relevance: {r['score']}]\n{r['text']}")
    return "\n\n---\n\n".join(parts)


def list_sources() -> list[dict]:
    """Return distinct document sources in the knowledge base."""
    try:
        client = _get_client()
        collection = _get_collection(client)
        all_meta = collection.get(include=["metadatas"])["metadatas"]
        seen = {}
        for m in all_meta:
            src = m.get("source", "unknown")
            if src not in seen:
                seen[src] = {"source": src, "type": m.get("type", "general"), "chunks": 0}
            seen[src]["chunks"] += 1
        return list(seen.values())
    except Exception:
        return []


def delete_source(source_name: str) -> int:
    """Delete all chunks from a named source. Returns count deleted."""
    try:
        client = _get_client()
        collection = _get_collection(client)
        results = collection.get(where={"source": source_name}, include=["metadatas"])
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return len(ids)
    except Exception:
        return 0


def get_stats() -> dict:
    """Return basic stats about the knowledge base."""
    try:
        client = _get_client()
        collection = _get_collection(client)
        count = collection.count()
        sources = list_sources()
        return {"total_chunks": count, "total_sources": len(sources)}
    except Exception:
        return {"total_chunks": 0, "total_sources": 0}
