---
id: "2026-03-19-mcpmodel-context-protocolってなんだ-aiと外部ツールをつなぐ国際空港を完全-01"
title: "MCP（Model Context Protocol）ってなんだ？ — AIと外部ツールをつなぐ「国際空港」を完全理解する"
url: "https://qiita.com/GeneLab_999/items/d1299630fc2c0325003b"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "LLM", "qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

## この記事の対象読者

- AIエージェントやLLMアプリケーションの開発に興味がある方
- `pip install` 感覚でAIにツール連携を追加したいエンジニア
- MCPという単語をよく見かけるが、正体がわからないままの方
- Function CallingやRAGとの違いを整理したい中級エンジニア

## この記事で得られること

- <font color="#00A1B3">MCPの仕組み・設計思想・アーキテクチャを体系的に理解できる</font>
- <font color="#00A1B3">Host / Client / Server / Transport の役割分担を図解で把握できる</font>
- <font color="#00A1B3">MCPの5つの基本要素（Tools, Resources, Prompts, Sampling, Elicitation）を理解できる</font>
- <font color="#00A1B3">Function Calling・RAG・OpenAPIとの違いを明確に区別できる</font>
- <font co
