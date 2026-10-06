"""Paths and defaults for the local RAG starter."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INDEX_PATH = ROOT / "index" / "store.json"
QUESTIONS_PATH = ROOT / "eval" / "questions.json"

CHUNK_SIZE = 320
CHUNK_OVERLAP = 60
NGRAM_MIN = 2
NGRAM_MAX = 3
DEFAULT_K = 3

# A hit is relevant when coverage clears the floor and cosine clears MIN_SCORE.
# Short queries dilute cosine against a long chunk, so a lower score is still
# accepted when the best section inside that chunk is a strong match.
MIN_SCORE = 0.12
MIN_COVERAGE = 0.2
SHORT_QUERY_MIN_SCORE = 0.08
SECTION_MIN_SCORE = 0.2

ABSTAIN_MESSAGE = "目前的語料庫無法支持這個問題的答案。"

INDEX_VERSION = 1
EMBEDDING_NAME = "tfidf-char-ngram"
