"""Build the FAISS index from knowledge/*.txt documents."""

from rag.pipeline import build_index

if __name__ == "__main__":
    index, chunks = build_index()
    print(f"Indexed {len(chunks)} chunks into rag/index/faiss.index")
