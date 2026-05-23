from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = SKILL_ROOT / "assets" / "graph" / "full_book" / "comporg_kg.sqlite"


def parse_json(value: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return value


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def row_value(row: sqlite3.Row, cols: set[str], key: str, default: Any = "") -> Any:
    return row[key] if key in cols else default


def row_to_node(row: sqlite3.Row, cols: set[str]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "type": row["type"],
        "name": row["name"],
        "aliases": parse_json(row["aliases"]),
        "definition": row["definition"],
        "source_pages": parse_json(row["source_pages"]),
        "source_chunk_id": row["source_chunk_id"],
        "evidence_text": row["evidence_text"],
        "confidence": row["confidence"],
        "chapter_num": row_value(row, cols, "chapter_num", None),
        "chapter": row_value(row, cols, "chapter", ""),
    }


def row_to_edge(row: sqlite3.Row, cols: set[str]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "source": row["source"],
        "target": row["target"],
        "type": row["type"],
        "description": row["description"],
        "source_pages": parse_json(row["source_pages"]),
        "source_chunk_id": row_value(row, cols, "source_chunk_id", ""),
        "evidence_text": row["evidence_text"],
        "confidence": row["confidence"],
        "chapter_num": row_value(row, cols, "chapter_num", None),
        "chapter": row_value(row, cols, "chapter", ""),
    }


def tokenize(text: str) -> list[str]:
    ascii_terms = re.findall(r"[a-zA-Z0-9_+\-.]+", text.lower())
    cjk_terms: list[str] = []
    for segment in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        parts = [p for p in re.split(r"和|与|及|或|的|区别|关系|比较|解释|说明", segment) if len(p) >= 2]
        cjk_terms.extend(parts)
        if len(segment) <= 8:
            cjk_terms.append(segment)
    return list(dict.fromkeys(ascii_terms + cjk_terms))


def resolve_db(db_arg: str) -> Path:
    env_db = os.environ.get("COMPORG_KG_DB")
    if env_db and db_arg == str(DEFAULT_DB):
        return Path(env_db).expanduser().resolve()
    db = Path(db_arg).resolve()
    return db


def search_nodes(conn: sqlite3.Connection, query: str, limit: int, chapter: int | None, node_type: str | None, node_cols: set[str]) -> list[dict[str, Any]]:
    terms = tokenize(query)
    where = []
    params: list[Any] = []
    if chapter is not None and "chapter_num" in node_cols:
        where.append("chapter_num = ?")
        params.append(chapter)
    if node_type:
        where.append("type = ?")
        params.append(node_type)
    sql = "SELECT * FROM nodes"
    if where:
        sql += " WHERE " + " AND ".join(where)
    rows = conn.execute(sql, params).fetchall()

    scored: list[tuple[int, sqlite3.Row]] = []
    for row in rows:
        haystack = "\n".join([row["name"], row["aliases"], row["definition"], row["evidence_text"], row_value(row, node_cols, "chapter", "")]).lower()
        score = 0
        if row["name"] and row["name"] in query:
            score += 30
        for alias in parse_json(row["aliases"]):
            if alias and alias in query:
                score += 24
        for term in terms:
            needle = term.lower()
            if needle in row["name"].lower():
                score += 10
            if needle in row["aliases"].lower():
                score += 8
            if needle in row["definition"].lower():
                score += 4
            if needle in haystack:
                score += 1
        if score:
            scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], row_value(item[1], node_cols, "chapter_num", 0) or 0, item[1]["type"], item[1]["name"]))
    return [row_to_node(row, node_cols) | {"score": score} for score, row in scored[:limit]]


def page_nodes(conn: sqlite3.Connection, page: int, chapter: int | None, node_type: str | None, node_cols: set[str]) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM nodes").fetchall()
    result = []
    for row in rows:
        if chapter is not None and "chapter_num" in node_cols and row["chapter_num"] != chapter:
            continue
        if node_type and row["type"] != node_type:
            continue
        pages = parse_json(row["source_pages"])
        if isinstance(pages, list) and pages:
            if len(pages) == 2 and isinstance(pages[0], int) and isinstance(pages[1], int):
                if pages[0] <= page <= pages[1]:
                    result.append(row_to_node(row, node_cols))
            elif page in pages:
                result.append(row_to_node(row, node_cols))
    return result


def neighbor_edges(conn: sqlite3.Connection, node_id: str, edge_cols: set[str]) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM edges WHERE source = ? OR target = ? ORDER BY type, id", (node_id, node_id)).fetchall()
    return [row_to_edge(row, edge_cols) for row in rows]


def subgraph(conn: sqlite3.Connection, nodes: list[dict[str, Any]], node_cols: set[str], edge_cols: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    node_ids = {node["id"] for node in nodes}
    edge_rows = conn.execute("SELECT * FROM edges").fetchall()
    edges = [row_to_edge(row, edge_cols) for row in edge_rows if row["source"] in node_ids or row["target"] in node_ids]
    for edge in edges:
        node_ids.add(edge["source"])
        node_ids.add(edge["target"])
    if not node_ids:
        return nodes, []
    placeholders = ",".join("?" for _ in node_ids)
    node_rows = conn.execute(f"SELECT * FROM nodes WHERE id IN ({placeholders})", tuple(node_ids)).fetchall()
    return [row_to_node(row, node_cols) for row in node_rows], edges


def suggested_followups(nodes: list[dict[str, Any]]) -> list[str]:
    names = list(dict.fromkeys(node["name"] for node in nodes[:5]))
    if not names:
        return ["换一个关键词查询知识图谱。"]
    return [f"解释{name}并引用源页" for name in names[:3]] + ["列出相关概念之间的关系"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the bundled Computer Organization knowledge graph for grounded answers.")
    parser.add_argument("query", nargs="?", help="Keyword or natural-language question.")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--chapter", type=int, help="Filter by chapter number.")
    parser.add_argument("--type", dest="node_type", help="Filter by node type, e.g. Concept, Formula, Component.")
    parser.add_argument("--page", type=int, help="Return nodes whose source_pages include this page.")
    parser.add_argument("--neighbors", help="Return edges adjacent to a node id.")
    args = parser.parse_args()

    db = resolve_db(args.db)
    if not db.exists():
        raise SystemExit(f"Knowledge graph database not found: {db}. Reinstall the skill with bundled assets or pass --db.")

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    node_cols = columns(conn, "nodes")
    edge_cols = columns(conn, "edges")

    if args.page is not None:
        nodes = page_nodes(conn, args.page, args.chapter, args.node_type, node_cols)
        matched_nodes = nodes
        edges: list[dict[str, Any]] = []
        query_label = f"page:{args.page}"
    elif args.neighbors:
        node = conn.execute("SELECT * FROM nodes WHERE id = ?", (args.neighbors,)).fetchone()
        nodes = [row_to_node(node, node_cols)] if node else []
        matched_nodes = nodes
        edges = neighbor_edges(conn, args.neighbors, edge_cols)
        query_label = f"neighbors:{args.neighbors}"
    else:
        if not args.query:
            raise SystemExit("Provide a query, --page, or --neighbors.")
        matched_nodes = search_nodes(conn, args.query, args.limit, args.chapter, args.node_type, node_cols)
        nodes, edges = subgraph(conn, matched_nodes, node_cols, edge_cols)
        query_label = args.query

    source_pages = []
    evidence_snippets = []
    matched_ids = {node["id"] for node in matched_nodes}
    evidence_nodes = matched_nodes + [node for node in nodes if node["id"] not in matched_ids]
    for node in evidence_nodes[: args.limit]:
        source_pages.extend(node.get("source_pages", []))
        if node.get("evidence_text"):
            evidence_snippets.append({"node_id": node["id"], "name": node["name"], "source_pages": node["source_pages"], "evidence_text": node["evidence_text"]})
    for edge in edges[: args.limit]:
        source_pages.extend(edge.get("source_pages", []))

    output = {
        "query": query_label,
        "matched_nodes": matched_nodes[: args.limit],
        "subgraph_edges": edges[: args.limit * 2],
        "source_pages": sorted({p for p in source_pages if isinstance(p, int)}),
        "evidence_snippets": evidence_snippets[: args.limit],
        "suggested_followups": suggested_followups(matched_nodes),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
