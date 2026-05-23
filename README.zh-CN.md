# comporg-knowledge-skill

[English](README.md) | 中文

`comporg-knowledge-skill` 是一个可复用的 Codex / Agent Skill 模板，用来把“带页码证据的知识图谱”封装成大模型可以本地查询、引用、讲解、出题和批改的工具。

这个项目来自一个私有教材蒸馏流程，但公开仓库只保留通用框架、脚本、schema、合成示例数据和 smoke test。仓库中不包含受版权保护的教材、OCR 页面、全文抽取结果、私有 API 配置或真实的全书蒸馏资产。

## 为什么需要它

大模型可以成为学习助手，但前提是它能区分“模型记忆”和“可追溯证据”。这个 skill 给 Agent 一个明确的工作约束：

> 先查询本地图谱，再基于源页和证据片段回答。

因此它适合教材、技术手册、规范、内部知识库等需要可追溯回答的场景。你可以把文档蒸馏成知识图谱，再让 Agent 使用这个 skill 做查证、讲解和测评。

## 仓库包含什么

- 单一 Codex / Agent Skill：`SKILL.md`
- Agent 配置：`agents/openai.yaml`
- 本地图谱查询脚本：`scripts/kg_query.py`
- 蒸馏资产查询脚本：`scripts/asset_query.py`
- 示例资产生成脚本：`scripts/build_sample_assets.py`
- Schema 与工作流说明：`references/`
- 合成示例图谱、QA、评测题和 skill notes：`assets/`
- 用于验证安装可用性的 smoke test

## 目录结构

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

## 快速开始

环境要求：

- Python 3.10+
- 示例流程不需要额外安装第三方 Python 包

生成示例资产并运行 smoke test：

```powershell
python .\scripts\build_sample_assets.py
python .\tests\smoke_test.py
```

查询示例知识图谱：

```powershell
python .\scripts\kg_query.py "cache" --limit 5
python .\scripts\kg_query.py "DMA" --chapter 8
python .\scripts\kg_query.py --page 206
python .\scripts\kg_query.py --neighbors sample_concept_cache
```

查询蒸馏学习资产：

```powershell
python .\scripts\asset_query.py "cache" --kind qa
python .\scripts\asset_query.py "pipeline" --kind eval --chapter 6
python .\scripts\asset_query.py "misconception" --kind notes
```

两个查询脚本都会输出 JSON，方便 Agent 直接消费结果。

## 接入自己的知识图谱

如果你已经把自己的教材、手册或规范蒸馏成图谱，可以替换这些示例资产：

```text
assets/graph/full_book/comporg_kg.sqlite
assets/graph/full_book/nodes.jsonl
assets/graph/full_book/edges.jsonl
assets/distilled/full_book/qa_items.jsonl
assets/distilled/full_book/eval_items.jsonl
assets/distilled/full_book/skill_notes.jsonl
```

如果你的真实资产较大或不适合放进仓库，也可以把数据库保留在外部路径，并通过环境变量指定：

```powershell
$env:COMPORG_KG_DB="D:\path\to\comporg_kg.sqlite"
python .\scripts\kg_query.py "interrupt" --chapter 8
```

SQLite 数据库需要提供与 `references/schema.md` 兼容的 `nodes` 和 `edges` 表。JSONL 蒸馏资产也应遵守同样的证据约定：每条事实、问答或评测项都应带有足够的页码和证据字段，便于 Agent 安全引用。

## 数据契约

图谱节点建议包含：

- `id`
- `type`
- `name`
- `aliases`
- `definition`
- `source_pages`
- `source_chunk_id`
- `evidence_text`
- `confidence`

图谱边建议包含：

- `id`
- `source`
- `target`
- `type`
- `description`
- `source_pages`
- `evidence_text`
- `confidence`

这个仓库中的脚本刻意保持轻量，定位是本地检索和 Agent 集成，不是生产级图数据库的替代品。

## 安装为 Codex Skill

将仓库复制或克隆到 Codex skills 目录，然后重启或刷新 Codex 的 skill 发现。

Windows 上的典型安装方式：

```powershell
Copy-Item -LiteralPath . -Destination "$env:USERPROFILE\.codex\skills\comporg-knowledge" -Recurse
```

安装后，skill 会要求 Agent：

- 回答事实问题前先查询图谱；
- 引用源页和证据片段；
- 生成讲解或测评时使用 QA、eval、skill notes 等蒸馏资产；
- 不仅凭模型记忆回答教材相关事实。

## 开源与版权边界

这个仓库可以公开发布，是因为它只包含合成示例数据和可复用代码。

不要公开提交：

- 原始教材、PDF、扫描页或页面图片；
- 从受版权保护材料中抽取的 OCR 文本或长段原文；
- 私有全量知识图谱、全量 QA 数据集或全量评测集；
- API key、base URL、模型调用日志、包含受保护原文的 prompt 或批处理 payload。

适合公开提交：

- 通用 skill 指令；
- schema 文档；
- 查询和验证脚本；
- 合成示例或明确授权的数据；
- 能证明 package 可用的测试。

## 开发与验证

提交前建议运行：

```powershell
python .\tests\smoke_test.py
```

smoke test 会重建合成示例资产，并验证：

- 图谱查询能返回匹配节点；
- 图谱查询结果包含源页信息；
- 蒸馏 QA 查询能返回示例条目。

## License

MIT。详见 `LICENSE`。

仓库内示例数据均为合成内容，只用于展示 schema 和工作流，不代表任何真实教材内容。
