"""Build, persist, and search the local JSON vector index."""

import json
from dataclasses import dataclass
from pathlib import Path

from rag_app.chunking import load_documents
from rag_app.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_NAME,
    INDEX_VERSION,
    NGRAM_MAX,
    NGRAM_MIN,
)
from rag_app.vectors import cosine, coverage, embed_query, fit_tfidf


@dataclass(frozen=True)
class Hit:
    id: str
    file: str
    title: str
    chunk_index: int
    text: str
    score: float
    coverage: float


@dataclass(frozen=True)
class Index:
    idf: dict[str, float]
    chunks: list[dict]
    chunk_size: int
    overlap: int

    def search(self, query: str, k: int) -> list[Hit]:
        if k <= 0:
            raise ValueError("k must be positive")
        query_vector = embed_query(query, self.idf)
        hits: list[Hit] = []
        for chunk in self.chunks:
            vector = chunk["vector"]
            terms = set(vector)
            hits.append(
                Hit(
                    id=chunk["id"],
                    file=chunk["file"],
                    title=chunk["title"],
                    chunk_index=int(chunk["chunk_index"]),
                    text=chunk["text"],
                    score=cosine(query_vector, vector),
                    coverage=coverage(query, terms, self.idf),
                )
            )
        hits.sort(key=lambda hit: (hit.score, hit.coverage), reverse=True)
        return hits[:k]


def build_index(data_dir: Path) -> tuple[Index, int]:
    documents = load_documents(data_dir)
    if not documents:
        raise FileNotFoundError(f"在 {data_dir} 找不到 .md、.markdown 或 .txt 文件")
    idf, vectors = fit_tfidf([doc["text"] for doc in documents])
    chunks: list[dict] = []
    for doc, vector in zip(documents, vectors, strict=True):
        chunks.append(
            {
                "id": doc["id"],
                "file": doc["file"],
                "title": doc["title"],
                "chunk_index": int(doc["chunk_index"]),
                "text": doc["text"],
                "vector": {term: round(weight, 6) for term, weight in sorted(vector.items())},
            }
        )
    index = Index(idf=idf, chunks=chunks, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    return index, len({doc["file"] for doc in documents})


def save_index(index: Index, path: Path) -> None:
    payload = {
        "version": INDEX_VERSION,
        "embedding": EMBEDDING_NAME,
        "ngram": [NGRAM_MIN, NGRAM_MAX],
        "chunk_size": index.chunk_size,
        "overlap": index.overlap,
        "idf": {term: round(weight, 6) for term, weight in sorted(index.idf.items())},
        "chunks": index.chunks,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_index(path: Path) -> Index:
    if not path.is_file():
        raise FileNotFoundError(f"找不到索引 {path}。請先執行 python -m rag_app ingest")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != INDEX_VERSION or payload.get("embedding") != EMBEDDING_NAME:
        raise ValueError(f"索引格式不符，請重新執行 python -m rag_app ingest：{path}")
    idf = {term: float(weight) for term, weight in payload["idf"].items()}
    return Index(
        idf=idf,
        chunks=payload["chunks"],
        chunk_size=int(payload["chunk_size"]),
        overlap=int(payload["overlap"]),
    )
