"""Grounded answers. The default path quotes chunks and needs no API key."""

import json
import os
import sys
import urllib.error
import urllib.request

from rag_app.config import ABSTAIN_MESSAGE, MIN_COVERAGE, MIN_SCORE
from rag_app.index import Hit

_TRUE = {"1", "true", "yes", "on"}


def llm_enabled() -> bool:
    return os.environ.get("RAG_LLM_ENABLED", "").strip().lower() in _TRUE


def relevant_hits(hits: list[Hit]) -> list[Hit]:
    if not hits:
        return []
    top = hits[0].score
    kept: list[Hit] = []
    for hit in hits:
        if hit.coverage < MIN_COVERAGE or hit.score < MIN_SCORE:
            continue
        if hit.score < top * 0.55:
            continue
        kept.append(hit)
    return kept


def extractive_answer(question: str, hits: list[Hit]) -> str:
    """Quote retrieved chunk text. Does not add facts that are not in the chunks."""
    lines = [
        f"問題：{question}",
        "",
        "根據檢索到的片段，摘錄如下：",
        "",
    ]
    for hit in hits:
        lines.append(f"[{hit.id}] {hit.title}")
        lines.append(hit.text.strip())
        lines.append("")
    return "\n".join(lines).rstrip()


def generate_answer(question: str, hits: list[Hit]) -> str:
    relevant = relevant_hits(hits)
    if not relevant:
        return ABSTAIN_MESSAGE
    if not llm_enabled():
        return extractive_answer(question, relevant)
    try:
        return _openai_compatible_answer(question, relevant)
    except Exception as exc:  # noqa: BLE001 — fall back to a grounded quote
        print(f"外部模型呼叫失敗，改以摘錄方式回答：{exc}", file=sys.stderr)
        return extractive_answer(question, relevant)


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
