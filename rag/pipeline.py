"""RAG pipeline: chunk → embed → FAISS store → retrieve."""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
INDEX_DIR = Path(__file__).resolve().parent / "index"
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_MODEL = None
_INDEX = None
_CHUNKS = None


def chunk_text(
    text: str,
    *,
    chunk_size: int = 400,
    overlap: int = 80,
    source: str = "",
) -> list[dict]:
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    index = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                {"text": piece, "source": source, "chunk_id": index}
            )
            index += 1
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def load_and_chunk_documents(
    knowledge_dir: str | Path,
    *,
    chunk_size: int = 400,
    overlap: int = 80,
) -> list[dict]:
    knowledge_dir = Path(knowledge_dir)
    all_chunks: list[dict] = []
    for path in sorted(knowledge_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(
            chunk_text(
                text,
                chunk_size=chunk_size,
                overlap=overlap,
                source=path.name,
            )
        )
    return all_chunks


def get_embedder():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def embed_texts(texts: list[str]) -> np.ndarray:
    vectors = get_embedder().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return np.asarray(vectors, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]


def build_index(
    knowledge_dir: Path | None = None,
    index_dir: Path | None = None,
) -> tuple[faiss.Index, list[dict]]:
    knowledge_dir = knowledge_dir or KNOWLEDGE_DIR
    index_dir = index_dir or INDEX_DIR
    index_dir.mkdir(parents=True, exist_ok=True)

    chunks = load_and_chunk_documents(knowledge_dir)
    if not chunks:
        raise RuntimeError(f"No documents found in {knowledge_dir}")

    vectors = embed_texts([c["text"] for c in chunks])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, str(index_dir / "faiss.index"))
    (index_dir / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    return index, chunks


def load_index(
    index_dir: Path | None = None,
) -> tuple[faiss.Index, list[dict]]:
    index_dir = index_dir or INDEX_DIR
    index_path = index_dir / "faiss.index"
    meta_path = index_dir / "chunks.json"

    if not index_path.exists() or not meta_path.exists():
        return build_index(index_dir=index_dir)

    index = faiss.read_index(str(index_path))
    chunks = json.loads(meta_path.read_text(encoding="utf-8"))
    return index, chunks


def search(
    query: str,
    *,
    top_k: int = 4,
    index: faiss.Index | None = None,
    chunks: list[dict] | None = None,
) -> list[dict]:
    if index is None or chunks is None:
        index, chunks = load_index()

    vector = embed_query(query).reshape(1, -1).astype("float32")
    scores, indices = index.search(vector, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        item = dict(chunks[int(idx)])
        item["score"] = float(score)
        results.append(item)
    return results


def ensure_index():
    global _INDEX, _CHUNKS
    if _INDEX is None or _CHUNKS is None:
        _INDEX, _CHUNKS = load_index()
    return _INDEX, _CHUNKS


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    index, chunks = ensure_index()
    return search(query, top_k=top_k, index=index, chunks=chunks)


def format_context(docs: list[dict]) -> str:
    if not docs:
        return "No relevant knowledge base passages found."
    parts = [
        f"[{i}] Source: {doc.get('source', 'unknown')}\n{doc.get('text', '')}"
        for i, doc in enumerate(docs, start=1)
    ]
    return "\n\n".join(parts)
