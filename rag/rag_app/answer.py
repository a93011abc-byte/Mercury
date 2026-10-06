"""Grounded answers. The default path quotes chunks and needs no API key."""

import json
import os
import sys
import urllib.error
import urllib.request

from rag_app.config import (
    ABSTAIN_MESSAGE,
    MIN_COVERAGE,
    MIN_SCORE,
    SECTION_MIN_SCORE,
    SHORT_QUERY_MIN_SCORE,
)
from rag_app.index import Hit
from rag_app.vectors import cosine, embed_query

_TRUE = {"1", "true", "yes", "on"}


def llm_enabled() -> bool:
    return os.environ.get("RAG_LLM_ENABLED", "").strip().lower() in _TRUE


def section_blocks(text: str) -> list[str]:
    """Split a chunk on Markdown headings. Each block keeps its heading and body."""
    blocks: list[str] = []
    buffer: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("#") and any(part.strip() for part in buffer):
            blocks.append("\n".join(buffer).strip())
            buffer = [line]
        else:
            buffer.append(line)
    if any(part.strip() for part in buffer):
        blocks.append("\n".join(buffer).strip())
    return blocks


def _section_scores(text: str, question: str, idf: dict[str, float]) -> list[tuple[float, str]]:
    query_vector = embed_query(question, idf)
    scored: list[tuple[float, str]] = []
    for block in section_blocks(text):
        scored.append((cosine(query_vector, embed_query(block, idf)), block))
    return scored


def _heading_only(block: str) -> bool:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    return len(lines) == 1 and lines[0].startswith("#")


def excerpt_for(question: str, hit: Hit, idf: dict[str, float]) -> str:
    """Quote the section of the chunk that overlaps the question. No new wording."""
    scored = _section_scores(hit.text, question, idf)
    if not scored:
        return hit.text.strip()
    best = max(score for score, _block in scored)
    if best <= 0:
        return hit.text.strip()
    floor = max(SECTION_MIN_SCORE, best * 0.65)
    chosen = {block for score, block in scored if score >= floor}
    ordered = [block for block in section_blocks(hit.text) if block in chosen]
    with_body = [block for block in ordered if not _heading_only(block)]
    if with_body:
        ordered = with_body
    return "\n\n".join(ordered)


def relevant_hits(question: str, hits: list[Hit], idf: dict[str, float]) -> list[Hit]:
    if not hits:
        return []
    kept: list[Hit] = []
    for hit in hits:
        if hit.coverage < MIN_COVERAGE:
            continue
        if hit.score >= MIN_SCORE:
            kept.append(hit)
            continue
        if hit.score < SHORT_QUERY_MIN_SCORE:
            continue
        section_score = max((score for score, _block in _section_scores(hit.text, question, idf)), default=0.0)
        if section_score >= SECTION_MIN_SCORE:
            kept.append(hit)
    if not kept:
        return []
    top = kept[0].score
    return [hit for hit in kept if hit.score >= top * 0.55]


def extractive_answer(question: str, hits: list[Hit], idf: dict[str, float]) -> str:
    """Quote retrieved text. Does not add facts that are not in the chunks."""
    lines = [
        f"問題：{question}",
        "",
        "根據檢索到的片段，摘錄如下：",
        "",
    ]
    excerpts = [(hit, excerpt_for(question, hit, idf)) for hit in hits]
    with_body = [(hit, excerpt) for hit, excerpt in excerpts if not _heading_only(excerpt)]
    chosen = with_body or excerpts
    seen: set[str] = set()
    for hit, excerpt in chosen:
        if excerpt in seen:
            continue
        seen.add(excerpt)
        lines.append(f"[{hit.id}] {hit.title}")
        lines.append(excerpt)
        lines.append("")
    return "\n".join(lines).rstrip()


def generate_answer(question: str, hits: list[Hit], idf: dict[str, float]) -> str:
    relevant = relevant_hits(question, hits, idf)
    if not relevant:
        return ABSTAIN_MESSAGE
    if not llm_enabled():
        return extractive_answer(question, relevant, idf)
    try:
        return _openai_compatible_answer(question, relevant)
    except Exception as exc:  # noqa: BLE001 — fall back to a grounded quote
        print(f"外部模型呼叫失敗，改以摘錄方式回答：{exc}", file=sys.stderr)
        return extractive_answer(question, relevant, idf)


def _openai_compatible_answer(question: str, hits: list[Hit]) -> str:
    base = os.environ.get("RAG_LLM_BASE_URL", "").strip().rstrip("/")
    api_key = os.environ.get("RAG_LLM_API_KEY", "").strip()
    model = os.environ.get("RAG_LLM_MODEL", "").strip() or "gpt-4o-mini"
    if not base or not api_key:
        raise RuntimeError("已設定 RAG_LLM_ENABLED，但缺少 RAG_LLM_BASE_URL 或 RAG_LLM_API_KEY")

    context = "\n\n".join(f"[{hit.id}] {hit.title}\n{hit.text.strip()}" for hit in hits)
    system = (
        "你是文件問答助手。只能根據使用者提供的片段回答，使用繁體中文。"
        "每個論點都要引用片段編號，格式如 [檔名#索引]。"
        "如果片段不足以回答，只能回覆這一句，不要加別的文字："
        f"{ABSTAIN_MESSAGE}"
        "不要補充片段裡沒有的事實。"
    )
    user = f"片段：\n{context}\n\n問題：{question}"
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    request = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code} {detail}") from exc
    content = body["choices"][0]["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("外部模型沒有回傳文字")
    return content.strip()
