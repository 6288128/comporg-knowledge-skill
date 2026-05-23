# comporg-knowledge-skill

一个可复用的 Codex / Agent Skill 模板，用于把“有页码依据的知识图谱”封装成大模型可查询、可讲解、可出题和可批改的本地工具。

这个仓库只包含通用 skill 框架、查询脚本、schema、示例数据和测试。真实教材 PDF、OCR 页面、全文图谱、QA 数据和私有 API 配置不应提交到公开仓库。

## 适合什么场景

- 你已经把一本教材、手册或规范蒸馏成 JSONL / SQLite 知识图谱。
- 你希望 Agent 回答前先查图谱，而不是只凭模型记忆。
- 你需要所有事实性回答都带 `source_pages` 和 `evidence_text`。
- 你想把查询、讲解、测评封装成一个可安装 skill。

## 目录结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── kg_query.py
│   ├── asset_query.py
│   └── build_sample_assets.py
├── references/
│   ├── schema.md
│   └── workflow-policy.md
├── assets/
│   ├── graph/full_book/
│   └── distilled/full_book/
└── tests/smoke_test.py
```

## 快速开始

```powershell
python .\scripts\build_sample_assets.py
python .\scripts\kg_query.py "cache" --limit 5
python .\scripts\asset_query.py "cache" --kind qa
python .\tests\smoke_test.py
```

如需接入自己的知识图谱，将下面文件替换成你的私有资产：

- `assets/graph/full_book/comporg_kg.sqlite`
- `assets/graph/full_book/nodes.jsonl`
- `assets/graph/full_book/edges.jsonl`
- `assets/distilled/full_book/qa_items.jsonl`
- `assets/distilled/full_book/eval_items.jsonl`
- `assets/distilled/full_book/skill_notes.jsonl`

也可以不复制数据，直接通过环境变量指定数据库：

```powershell
$env:COMPORG_KG_DB="D:\path\to\comporg_kg.sqlite"
python .\scripts\kg_query.py "DMA" --chapter 8
```

## 开源边界

请不要公开提交：

- 原始教材 PDF、页面截图、OCR 全文。
- 从受版权保护教材抽取的长段原文、全量 QA 或全量图谱。
- API key、base URL、模型调用日志、批处理 job 原文。
- 任何无法确认授权的数据资产。

推荐公开提交：

- Skill 工作流、查询脚本、schema、测试。
- 少量自造或明确可公开授权的示例数据。
- 资产生成脚本和接入说明。

## License

MIT。示例数据为演示用途，不代表任何真实教材内容。
