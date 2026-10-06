"""Command line: ingest, ask, and retrieval recall@k."""

import argparse
import json
import sys
from pathlib import Path

from rag_app.answer import generate_answer
from rag_app.config import DATA_DIR, DEFAULT_K, INDEX_PATH, QUESTIONS_PATH
from rag_app.index import build_index, load_index, save_index


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.cmd == "ingest":
            return _ingest(args.data, args.index)
        if args.cmd == "ask":
            return _ask(args.question, args.k, args.index)
        if args.cmd == "eval":
            return _eval(args.questions, args.index, args.k)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    parser.error(f"未知指令：{args.cmd}")
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag_app",
        description="離線可跑的 RAG 入門程式：本地切塊、TF-IDF 向量、摘錄回答。",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    ingest = sub.add_parser("ingest", help="讀取 data/，全量重建本地向量索引")
    ingest.add_argument("--data", type=Path, default=DATA_DIR)
    ingest.add_argument("--index", type=Path, default=INDEX_PATH)

    ask = sub.add_parser("ask", help="檢索 top-k 並回答；沒有相關片段就拒絕回答")
    ask.add_argument("question")
    ask.add_argument("--k", type=int, default=DEFAULT_K)
    ask.add_argument("--index", type=Path, default=INDEX_PATH)

    evaluate = sub.add_parser("eval", help="依預期來源檔計算 retrieval recall@k")
    evaluate.add_argument("--questions", type=Path, default=QUESTIONS_PATH)
    evaluate.add_argument("--index", type=Path, default=INDEX_PATH)
    evaluate.add_argument("--k", type=int, default=None, help="覆寫題目檔裡的 k")
    return parser


def _ingest(data_dir: Path, index_path: Path) -> int:
    index, file_count = build_index(data_dir)
    save_index(index, index_path)
    print(f"已索引 {file_count} 個檔案、{len(index.chunks)} 個片段，寫入 {index_path}")
    return 0


def _ask(question: str, k: int, index_path: Path) -> int:
    if k <= 0:
        print("k 必須是正整數", file=sys.stderr)
        return 2
    index = load_index(index_path)
    answer = generate_answer(question, index.search(question, k), index.idf)
    print(answer)
    return 0


def _eval(questions_path: Path, index_path: Path, k_override: int | None) -> int:
    if not questions_path.is_file():
        print(f"找不到題目檔 {questions_path}", file=sys.stderr)
        return 1
    payload = json.loads(questions_path.read_text(encoding="utf-8"))
    questions = payload["questions"]
    k = k_override if k_override is not None else int(payload.get("k", DEFAULT_K))
    if k <= 0:
        print("k 必須是正整數", file=sys.stderr)
        return 2
    index = load_index(index_path)

    recalls: list[float] = []
    print(f"retrieval recall@{k}")
    for item in questions:
        question_id = item["id"]
        question = item["question"]
        expected = list(dict.fromkeys(item["expected_files"]))
        hits = index.search(question, k)
        retrieved = list(dict.fromkeys(hit.file for hit in hits))
        recall = _recall(retrieved, expected)
        recalls.append(recall)
        top = hits[0] if hits else None
        score = f"{top.score:.3f}" if top else "-"
        print(
            f"{question_id}  recall={recall:.3f}  score={score}  "
            f"expected={','.join(expected)}  retrieved={','.join(retrieved) or '-'}"
        )
    macro = sum(recalls) / len(recalls) if recalls else 0.0
    print(f"retrieval recall@{k} = {macro:.3f}  ({len(recalls)} questions)")
    return 0 if macro == 1.0 else 1


def _recall(retrieved: list[str], expected: list[str]) -> float:
    if not expected:
        return 0.0
    found = set(retrieved) & set(expected)
    return len(found) / len(set(expected))


if __name__ == "__main__":
    raise SystemExit(main())
