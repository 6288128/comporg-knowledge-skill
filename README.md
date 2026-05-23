# comporg-knowledge-skill

`comporg-knowledge-skill` is a reusable Codex / Agent Skill template for turning a page-grounded knowledge graph into a local tool that language-model agents can query, cite, teach from, and assess against.

The project was extracted from a private textbook-distillation workflow. The public repository intentionally contains only the reusable framework, scripts, schema, synthetic sample assets, and smoke tests. It does **not** include copyrighted textbooks, OCR pages, full extracted text, private API configuration, or real full-book distillation outputs.

## Why This Exists

LLMs are useful study assistants only when they can separate memory from evidence. This skill gives an agent a simple rule and a simple interface:

> Search the local graph first, then answer with source pages and evidence snippets.

That makes it suitable for textbooks, manuals, standards, internal runbooks, and other structured documents where answers should be traceable.

## What Is Included

- A single Codex / Agent Skill: `SKILL.md`
- Agent configuration: `agents/openai.yaml`
- A local graph query script: `scripts/kg_query.py`
- A distilled-asset query script: `scripts/asset_query.py`
- A sample asset builder: `scripts/build_sample_assets.py`
- Schema and workflow references under `references/`
- Synthetic sample graph and QA/eval/notes assets under `assets/`
- A smoke test that verifies the skill can query bundled sample data

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── graph/full_book/
│   │   ├── comporg_kg.sqlite
│   │   ├── nodes.jsonl
│   │   ├── edges.jsonl
│   │   └── schema.json
│   └── distilled/full_book/
│       ├── qa_items.jsonl
│       ├── eval_items.jsonl
│       └── skill_notes.jsonl
├── references/
│   ├── schema.md
│   └── workflow-policy.md
├── scripts/
│   ├── asset_query.py
│   ├── build_sample_assets.py
│   └── kg_query.py
└── tests/
    └── smoke_test.py
```

## Quick Start

Requirements:

- Python 3.10+
- No external Python packages are required for the bundled sample workflow

Run the sample build and smoke test:

```powershell
python .\scripts\build_sample_assets.py
python .\tests\smoke_test.py
```

Query the sample knowledge graph:

```powershell
python .\scripts\kg_query.py "cache" --limit 5
python .\scripts\kg_query.py "DMA" --chapter 8
python .\scripts\kg_query.py --page 206
python .\scripts\kg_query.py --neighbors sample_concept_cache
```

Query distilled study assets:

```powershell
python .\scripts\asset_query.py "cache" --kind qa
python .\scripts\asset_query.py "pipeline" --kind eval --chapter 6
python .\scripts\asset_query.py "misconception" --kind notes
```

Both query scripts print JSON so agents can consume the output directly.

## Using Your Own Knowledge Graph

Replace the bundled synthetic assets with your private or licensed assets:

```text
assets/graph/full_book/comporg_kg.sqlite
assets/graph/full_book/nodes.jsonl
assets/graph/full_book/edges.jsonl
assets/distilled/full_book/qa_items.jsonl
assets/distilled/full_book/eval_items.jsonl
assets/distilled/full_book/skill_notes.jsonl
```

You can also keep large or private assets outside the repository and point the query script to them:

```powershell
$env:COMPORG_KG_DB="D:\path\to\comporg_kg.sqlite"
python .\scripts\kg_query.py "interrupt" --chapter 8
```

The SQLite database is expected to expose `nodes` and `edges` tables compatible with the fields documented in `references/schema.md`. JSONL files should follow the same source-grounding convention: every item should carry enough page and evidence metadata for an agent to cite it safely.

## Data Contract

Graph nodes should include:

- `id`
- `type`
- `name`
- `aliases`
- `definition`
- `source_pages`
- `source_chunk_id`
- `evidence_text`
- `confidence`

Graph edges should include:

- `id`
- `source`
- `target`
- `type`
- `description`
- `source_pages`
- `evidence_text`
- `confidence`

The bundled scripts are deliberately lightweight. They are designed for local retrieval and agent integration, not as a replacement for a production graph database.

## Installing as a Codex Skill

Copy or clone this repository into your Codex skills directory, then restart or refresh Codex skill discovery.

Typical Windows location:

```powershell
Copy-Item -LiteralPath . -Destination "$env:USERPROFILE\.codex\skills\comporg-knowledge" -Recurse
```

After installation, the skill instructs the agent to:

- query the graph before answering factual questions;
- cite source pages and evidence snippets;
- use distilled QA/eval/notes assets when generating explanations or assessments;
- avoid answering textbook-specific facts purely from model memory.

## Publication and Copyright Boundary

This repository is safe to publish because it contains synthetic sample data and reusable code only.

Do not publish:

- original textbooks, PDFs, scans, or page images;
- OCR text or long extracted passages from copyrighted sources;
- full private knowledge graphs or full QA datasets derived from restricted material;
- API keys, base URLs, model logs, prompts containing protected source text, or batch job payloads.

Recommended public assets:

- generic skill instructions;
- schema documentation;
- query and validation scripts;
- synthetic or clearly licensed examples;
- tests that prove the package works without private data.

## Development

Run the smoke test before committing:

```powershell
python .\tests\smoke_test.py
```

The smoke test rebuilds the synthetic sample assets and verifies that:

- graph queries return matched nodes;
- graph query results include source pages;
- distilled QA queries return sample items.

## License

MIT. See `LICENSE`.

The bundled sample data is synthetic and provided only to demonstrate the expected schema and workflow.
