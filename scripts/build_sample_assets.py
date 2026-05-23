from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAPH_DIR = ROOT / "assets" / "graph" / "full_book"
DISTILLED_DIR = ROOT / "assets" / "distilled" / "full_book"


NODES = [
    {
        "id": "sample_ch01",
        "type": "Chapter",
        "name": "Sample Chapter 1",
        "aliases": ["chapter one"],
        "definition": "Synthetic sample chapter for demonstrating graph-backed learning.",
        "source_pages": [1, 12],
        "source_chunk_id": "sample_chunk_001",
        "evidence_text": "Synthetic evidence: this chapter introduces processor and memory examples.",
        "confidence": 1.0,
        "provenance": "synthetic-sample",
        "chapter_num": 1,
        "chapter": "Sample Chapter 1"
    },
    {
        "id": "sample_concept_cache",
        "type": "Concept",
        "name": "cache",
        "aliases": ["cache memory", "高速缓存"],
        "definition": "A small fast storage layer that keeps recently or frequently used data near the processor.",
        "source_pages": [101],
        "source_chunk_id": "sample_chunk_cache",
        "evidence_text": "Synthetic evidence: cache improves average access time by storing likely reused data near the CPU.",
        "confidence": 0.98,
        "provenance": "synthetic-sample",
        "chapter_num": 7,
        "chapter": "Sample Chapter 7"
    },
    {
        "id": "sample_metric_amat",
        "type": "Metric",
        "name": "average memory access time",
        "aliases": ["AMAT", "平均访存时间"],
        "definition": "A metric combining cache hit time, miss rate, and miss penalty.",
        "source_pages": [102],
        "source_chunk_id": "sample_chunk_amat",
        "evidence_text": "Synthetic evidence: AMAT combines hit time with miss behavior.",
        "confidence": 0.95,
        "provenance": "synthetic-sample",
        "chapter_num": 7,
        "chapter": "Sample Chapter 7"
    },
    {
        "id": "sample_formula_amat",
        "type": "Formula",
        "name": "AMAT formula",
        "aliases": ["AMAT = hit time + miss rate * miss penalty"],
        "definition": "Average memory access time equals hit time plus miss rate multiplied by miss penalty.",
        "source_pages": [102],
        "source_chunk_id": "sample_chunk_amat",
        "evidence_text": "Synthetic evidence: AMAT = hit time + miss rate * miss penalty.",
        "confidence": 0.95,
        "provenance": "synthetic-sample",
        "chapter_num": 7,
        "chapter": "Sample Chapter 7"
    },
    {
        "id": "sample_technique_dma",
        "type": "Technique",
        "name": "DMA",
        "aliases": ["direct memory access", "直接存储器访问"],
        "definition": "An I/O technique that transfers blocks between device and memory with reduced CPU involvement.",
        "source_pages": [201],
        "source_chunk_id": "sample_chunk_dma",
        "evidence_text": "Synthetic evidence: DMA lets a controller move data blocks between memory and I/O devices.",
        "confidence": 0.96,
        "provenance": "synthetic-sample",
        "chapter_num": 8,
        "chapter": "Sample Chapter 8"
    }
]


EDGES = [
    {
        "id": "sample_edge_cache_measured_by_amat",
        "source": "sample_concept_cache",
        "target": "sample_metric_amat",
        "type": "measured_by",
        "description": "Cache behavior can be evaluated with average memory access time.",
        "source_pages": [102],
        "source_chunk_id": "sample_chunk_amat",
        "evidence_text": "Synthetic evidence: AMAT combines cache hit and miss behavior.",
        "confidence": 0.94,
        "provenance": "synthetic-sample",
        "chapter_num": 7,
        "chapter": "Sample Chapter 7"
    },
    {
        "id": "sample_edge_formula_for_amat",
        "source": "sample_formula_amat",
        "target": "sample_metric_amat",
        "type": "formula_for",
        "description": "The formula defines the AMAT metric.",
        "source_pages": [102],
        "source_chunk_id": "sample_chunk_amat",
        "evidence_text": "Synthetic evidence: AMAT = hit time + miss rate * miss penalty.",
        "confidence": 0.95,
        "provenance": "synthetic-sample",
        "chapter_num": 7,
        "chapter": "Sample Chapter 7"
    },
    {
        "id": "sample_edge_dma_used_in_io",
        "source": "sample_technique_dma",
        "target": "sample_ch01",
        "type": "used_in",
        "description": "DMA is a technique used in system-level I/O discussions.",
        "source_pages": [201],
        "source_chunk_id": "sample_chunk_dma",
        "evidence_text": "Synthetic evidence: DMA is discussed as an I/O data transfer technique.",
        "confidence": 0.9,
        "provenance": "synthetic-sample",
        "chapter_num": 8,
        "chapter": "Sample Chapter 8"
    }
]


QA = [
    {
        "id": "sample_qa_cache_1",
        "question": "What does a cache try to improve?",
        "answer": "It tries to improve average access time by keeping likely reused data near the processor.",
        "reasoning_brief": "The sample evidence connects cache with average access time.",
        "difficulty": "easy",
        "source_pages": [101, 102],
        "tags": ["cache", "AMAT"],
        "evidence_node_ids": ["sample_concept_cache", "sample_metric_amat"],
        "chapter_num": 7,
        "chapter": "Sample Chapter 7",
        "source_chunk_id": "sample_chunk_cache",
        "provenance": "synthetic-sample"
    }
]


EVALS = [
    {
        "id": "sample_eval_amat_1",
        "input": "Explain why miss rate affects average memory access time.",
        "expected_points": ["Mention hit time", "Mention miss rate", "Mention miss penalty"],
        "source_pages": [102],
        "rubric": {"hit_time": 1, "miss_rate": 1, "miss_penalty": 1},
        "task_type": "conceptual",
        "chapter_num": 7,
        "chapter": "Sample Chapter 7",
        "source_chunk_id": "sample_chunk_amat",
        "provenance": "synthetic-sample"
    }
]


NOTES = [
    {
        "id": "sample_note_query_first",
        "topic": "query-first tutoring",
        "note": "Always query the graph before giving a source-grounded explanation.",
        "source_pages": [101],
        "chapter_num": 7,
        "chapter": "Sample Chapter 7",
        "source_chunk_id": "sample_chunk_cache",
        "provenance": "synthetic-sample"
    }
]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def create_sqlite(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            type TEXT,
            name TEXT,
            aliases TEXT,
            definition TEXT,
            source_pages TEXT,
            source_chunk_id TEXT,
            evidence_text TEXT,
            confidence REAL,
            provenance TEXT,
            chapter_num INTEGER,
            chapter TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE edges (
            id TEXT PRIMARY KEY,
            source TEXT,
            target TEXT,
            type TEXT,
            description TEXT,
            source_pages TEXT,
            source_chunk_id TEXT,
            evidence_text TEXT,
            confidence REAL,
            provenance TEXT,
            chapter_num INTEGER,
            chapter TEXT
        )
        """
    )
    for node in NODES:
        conn.execute(
            "INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                node["id"],
                node["type"],
                node["name"],
                json.dumps(node["aliases"], ensure_ascii=False),
                node["definition"],
                json.dumps(node["source_pages"], ensure_ascii=False),
                node["source_chunk_id"],
                node["evidence_text"],
                node["confidence"],
                node["provenance"],
                node["chapter_num"],
                node["chapter"],
            ),
        )
    for edge in EDGES:
        conn.execute(
            "INSERT INTO edges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                edge["id"],
                edge["source"],
                edge["target"],
                edge["type"],
                edge["description"],
                json.dumps(edge["source_pages"], ensure_ascii=False),
                edge["source_chunk_id"],
                edge["evidence_text"],
                edge["confidence"],
                edge["provenance"],
                edge["chapter_num"],
                edge["chapter"],
            ),
        )
    conn.commit()
    conn.close()


def main() -> None:
    write_jsonl(GRAPH_DIR / "nodes.jsonl", NODES)
    write_jsonl(GRAPH_DIR / "edges.jsonl", EDGES)
    write_jsonl(DISTILLED_DIR / "qa_items.jsonl", QA)
    write_jsonl(DISTILLED_DIR / "eval_items.jsonl", EVALS)
    write_jsonl(DISTILLED_DIR / "skill_notes.jsonl", NOTES)
    (GRAPH_DIR / "finalization_summary.json").write_text(
        json.dumps(
            {
                "scope": "synthetic sample",
                "chapters": 3,
                "nodes": len(NODES),
                "edges": len(EDGES),
                "qa_items": len(QA),
                "eval_items": len(EVALS),
                "skill_notes": len(NOTES),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    create_sqlite(GRAPH_DIR / "comporg_kg.sqlite")
    print(f"Wrote sample assets to {ROOT}")


if __name__ == "__main__":
    main()
