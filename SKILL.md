---
name: comporg-knowledge
description: 使用本地知识图谱和蒸馏资产进行查询、讲解、出题和批改。适用于需要页码引用、证据片段、学习辅导、测验生成和答案评估的教材或手册型知识库。
---

# 知识图谱学习助手

当用户询问某本教材、手册或规范中的事实、概念、公式、例题、练习或学习路径时，使用这个 skill。

## 核心规则

回答事实性问题前必须先查询本地知识图谱或蒸馏资产。不要只凭模型记忆回答。凡是来自资料的事实性说法，都应引用查询结果中的 `source_pages` 和 `evidence_text`。

## 内置资源

本开源版本只附带少量自造示例数据，用于演示接口和测试。真实项目应替换为自己的私有图谱资产。

- 图谱数据库：`assets/graph/full_book/comporg_kg.sqlite`
- 图谱 JSONL：`assets/graph/full_book/nodes.jsonl`、`assets/graph/full_book/edges.jsonl`
- 蒸馏资产：`assets/distilled/full_book/qa_items.jsonl`、`eval_items.jsonl`、`skill_notes.jsonl`
- 查询脚本：`scripts/kg_query.py`、`scripts/asset_query.py`
- 结构和策略说明：`references/schema.md`、`references/workflow-policy.md`

## 使用模式

### 查证

用于概念检索、关系追踪、页码查证、邻接节点展开和 JSON 证据返回。

```powershell
python .\scripts\kg_query.py "cache" --limit 8
python .\scripts\kg_query.py "DMA" --chapter 8 --limit 8
python .\scripts\kg_query.py --page 101 --limit 8
python .\scripts\kg_query.py --neighbors sample_concept_cache
```

### 讲解

1. 先用学习者关键词查询图谱。
2. 再查询蒸馏资产中的既有问答或 skill notes。
3. 按“直观理解、准确定义、机制或公式、相关关系、常见误区”的顺序讲解。
4. 正文中引用页码，例如 `页 101`。
5. 需要时用 1-3 个自测题收尾。

### 测评

1. 查询主题相关的图谱证据和邻接关系。
2. 查询 `eval` 和 `qa` 蒸馏资产。
3. 只基于图谱证据、边关系和蒸馏评测条目出题或批改。
4. 输出源页码和得分点。
5. 批改时区分“正确点、遗漏点、无依据说法”。

## 输出格式

直接查证时，可以返回简洁 JSON，也可以基于查询结果给出短答。

教学讲解时，优先使用这些小节：`结论`、`依据`、`解释`、`易错点`、`自测`。

生成题目时，每题包含：

`question`、`type`、`difficulty`、`expected_points`、`rubric`、`source_pages`、`evidence_node_ids`

批改答案时，包含：

`score`、`max_score`、`correct_points`、`missing_points`、`unsupported_claims`、`source_pages`
