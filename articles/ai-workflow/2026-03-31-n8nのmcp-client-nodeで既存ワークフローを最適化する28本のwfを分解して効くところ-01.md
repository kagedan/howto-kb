---
id: "2026-03-31-n8nのmcp-client-nodeで既存ワークフローを最適化する28本のwfを分解して効くところ-01"
title: "n8nのMCP Client Nodeで既存ワークフローを最適化する——28本のWFを分解して「効くところ」だけMCP化した話"
url: "https://qiita.com/murata-seiji/items/41c18cbca6508acbed5e"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

n8n v2.13でMCP Client Nodeが追加された。

「お、ついに来たか」と思って、うちの28本のワークフローを全部分解してみた。HTTP Requestノードが合計70個。こいつらのうち、どれをMCP Client Nodeに置き換えたら幸せになれるのか。

結論から言うと、**MCP化して意味があるのは6本だけだった**。残り22本は今のままでいい。

日本語の記事を探してみたが、MCP Client Nodeの基本的な使い方を紹介しているものはあっても、「既存WFを全部棚卸しして、どこにMCPを入れるべきか判断した」という記事は見つからなかった。だから書く。

## MCP Client Nodeとは何か

n8n v2.13.xで追加された`@n8n/n8n-nodes-langchain.mcpClientTool`のこと。（[公式ドキュメント](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/)）

ワークフローの中から、外
