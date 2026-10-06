"""Split documents into overlapping chunks with source metadata."""

from pathlib import Path

from rag_app.config import CHUNK_OVERLAP, CHUNK_SIZE


def extract_title(text: str, file_id: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if title:
                return title
    return Path(file_id).stem


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Slide a window over text.

    Windows prefer to end on a newline. The next window starts `overlap`
    characters before the previous end so a sentence on the boundary stays
    retrievable in both chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        if end < len(normalized):
            window = normalized[start:end]
            break_at = window.rfind("\n\n")
            if break_at < chunk_size // 2:
                break_at = window.rfind("\n")
            if break_at >= chunk_size // 2:
                end = start + break_at
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(normalized):
            break
        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1
        start = next_start
    return chunks


def load_documents(data_dir: Path) -> list[dict[str, str]]:
    """Read markdown and text files under data_dir.

    `file` is the path relative to data_dir, using forward slashes.
    """
    patterns = ("*.md", "*.markdown", "*.txt")
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(data_dir.rglob(pattern))
    documents: list[dict[str, str]] = []
    for path in sorted(set(paths)):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(data_dir).parts):
            continue
        file_id = path.relative_to(data_dir).as_posix()
        text = path.read_text(encoding="utf-8")
        title = extract_title(text, file_id)
        for index, piece in enumerate(chunk_text(text)):
            documents.append(
                {
                    "id": f"{file_id}#{index}",
                    "file": file_id,
                    "title": title,
                    "chunk_index": str(index),
                    "text": piece,
                }
            )
    return documents
