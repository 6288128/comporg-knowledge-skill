from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DISTILLED_DIR = SKILL_ROOT / "assets" / "distilled" / "full_book"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_chapters(value: str | None) -> set[int] | None:
    if not value:
        return None
    if value.lower() == "all":
        return None
    return {int(part.strip()) for part in value.split(",") if part.strip()}


def score_row(row: dict[str, Any], query: str) -> int:
    haystack = json.dumps(row, ensure_ascii=False).lower()
    terms = re.findall(r"[a-zA-Z0-9_+\-.]+|[\u4e00-\u9fff]{2,}", query.lower())
    score = 0
    for term in terms:
        if term in haystack:
            score += 1
    if query and query in haystack:
        score += 10
    return score


def load_sources(kind: str, root: Path) -> list[tuple[str, list[dict[str, Any]]]]:
    sources = []
    if kind in {"all", "qa"}:
        sources.append(("qa", read_jsonl(root / "qa_items.jsonl")))
    if kind in {"all", "eval"}:
        sources.append(("eval", read_jsonl(root / "eval_items.jsonl")))
    if kind in {"all", "notes"}:
        sources.append(("notes", read_jsonl(root / "skill_notes.jsonl")))
    return sources


def main() -> None:
    parser = argparse.ArgumentParser(description="Query bundled distilled QA, evals, and skill notes.")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--kind", choices=["all", "qa", "eval", "notes"], default="all")
    parser.add_argument("--chapter", help="Chapter number filter, e.g. 7 or 1,2,6.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--distilled-dir", default=str(DEFAULT_DISTILLED_DIR))
    args = parser.parse_args()

    root = Path(args.distilled_dir).resolve()
    if not root.exists():
        raise SystemExit(f"Distilled assets not found: {root}. Reinstall the skill with bundled assets or pass --distilled-dir.")

    chapters = parse_chapters(args.chapter)
    results: list[dict[str, Any]] = []
    for source, rows in load_sources(args.kind, root):
        for row in rows:
            if chapters is not None and int(row.get("chapter_num") or -1) not in chapters:
                continue
            score = score_row(row, args.query) if args.query else 1
            if score:
                results.append({"source": source, "score": score, "item": row})
    results.sort(key=lambda item: (-item["score"], item["source"], item["item"].get("id", "")))
    print(json.dumps({"query": args.query, "kind": args.kind, "results": results[: args.limit]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
