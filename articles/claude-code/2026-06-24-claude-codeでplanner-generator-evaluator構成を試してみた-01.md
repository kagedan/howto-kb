---
id: "2026-06-24-claude-codeでplanner-generator-evaluator構成を試してみた-01"
title: "Claude CodeでPlanner / Generator / Evaluator構成を試してみた"
url: "https://zenn.dev/yuki_engineer08/articles/cef70ea4a9a98f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-06-24"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

Claude Codeを使った開発で感じたのは、

「1つのAIに全部やらせるとレビューが弱い」

ということでした。

そこで、

Planner（要件整理）  
Generator（実装）  
Evaluator（レビュー）

の3エージェント構成を作ってみました。

役割を完全に分離し、

・Planner → SPEC.mdからタスク分解  
・Generator → 実装のみ担当  
・Evaluator → 批判的レビュー担当

という流れで開発を進めます。

実際にNext.js + Terraform + CloudFront構成の技術ブログ開発で利用したところ、

CloudFront Function関連の不備  
GitHub ActionsのOIDC設定漏れ  
Terraform管理外リソース

などを早い段階で発見できました。

単一AIよりも「複数視点で確認できる」ことが最大のメリットだと感じています。

詳しい構成や運用方法はブログにまとめました。  
<https://d3o7t81m8nyt3g.cloudfront.net/blog/2026-06-24-caregiver-built-ai-team-with-claude-code>
