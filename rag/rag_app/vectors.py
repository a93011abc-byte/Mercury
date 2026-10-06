"""Local character n-gram TF-IDF vectors. No model download."""

import math
import re
from collections import Counter

from rag_app.config import NGRAM_MAX, NGRAM_MIN

_NON_WORD = re.compile(r"[^\w]+", re.UNICODE)


def normalize(text: str) -> str:
    return _NON_WORD.sub("", text.lower())


def ngrams(text: str, nmin: int = NGRAM_MIN, nmax: int = NGRAM_MAX) -> list[str]:
    compacted = normalize(text)
    grams: list[str] = []
    for n in range(nmin, nmax + 1):
        if len(compacted) < n:
            continue
        grams.extend(compacted[i : i + n] for i in range(len(compacted) - n + 1))
    return grams


def _l2_normalize(weights: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(value * value for value in weights.values()))
    if norm == 0:
        return {}
    return {term: value / norm for term, value in weights.items()}


def fit_tfidf(texts: list[str]) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Fit smoothed TF-IDF on chunk texts and return L2-normalized sparse vectors.

    N-grams that occur in every chunk are dropped when there is more than one
    chunk, because they cannot separate documents.
    """
    counts = [Counter(ngrams(text)) for text in texts]
    total = len(counts)
    doc_freq: Counter[str] = Counter()
    for count in counts:
        doc_freq.update(count.keys())

    idf: dict[str, float] = {}
    for term, freq in doc_freq.items():
        if total >= 2 and freq >= total:
            continue
        idf[term] = math.log((total + 1) / (freq + 1)) + 1.0

    vectors = [_tfidf_vector(count, idf) for count in counts]
    return idf, vectors


def embed_query(text: str, idf: dict[str, float]) -> dict[str, float]:
    return _tfidf_vector(Counter(ngrams(text)), idf)


def _tfidf_vector(counts: Counter[str], idf: dict[str, float]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for term, freq in counts.items():
        if freq <= 0 or term not in idf:
            continue
        weights[term] = (1.0 + math.log(freq)) * idf[term]
    return _l2_normalize(weights)


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(term, 0.0) for term, value in left.items())


def coverage(query: str, chunk_terms: set[str], idf: dict[str, float]) -> float:
    """Share of the query's IDF mass that appears in the chunk.

    Query n-grams that were never seen in the corpus (or were dropped as
    non-discriminative) do not count. An out-of-corpus question therefore
    scores 0 and the answerer abstains.
    """
    total = 0.0
    matched = 0.0
    for term in set(ngrams(query)):
        weight = idf.get(term)
        if not weight:
            continue
        total += weight
        if term in chunk_terms:
            matched += weight
    if total == 0:
        return 0.0
    return matched / total
