# Workflow Policy

## Query First

For textbook-grounded answers, query `kg_query.py` before explaining. Use `asset_query.py` when you need existing QA, eval items, or skill notes.

## Citation

Every factual claim that depends on source material should include page references from `source_pages`. Prefer short evidence snippets over long quotation.

## Tutoring

Use a compact structure:

1. Conclusion.
2. Evidence.
3. Explanation.
4. Common mistakes.
5. Optional self-check.

## Assessment

When generating or grading questions, include expected points, rubric, source pages, and evidence node ids. Mark unsupported claims separately.
