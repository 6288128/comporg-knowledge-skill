# Graph Schema

## Node Fields

- `id`: stable node id.
- `type`: one of `Chapter`, `Section`, `Concept`, `Metric`, `Formula`, `Hazard`, `Technique`, `Component`, `Instruction`, `Example`, `Exercise`.
- `name`: display name.
- `aliases`: JSON array of alternative names.
- `definition`: concise explanation.
- `source_pages`: JSON array of page numbers or a two-number range.
- `source_chunk_id`: source chunk id.
- `evidence_text`: short evidence snippet.
- `confidence`: number between 0 and 1.
- `provenance`: source of the extraction or review.

## Edge Fields

- `id`: stable edge id.
- `source`: source node id.
- `target`: target node id.
- `type`: relationship type.
- `description`: concise relation explanation.
- `source_pages`: JSON array of page numbers or a two-number range.
- `source_chunk_id`: source chunk id.
- `evidence_text`: short evidence snippet.
- `confidence`: number between 0 and 1.
- `provenance`: source of the extraction or review.
