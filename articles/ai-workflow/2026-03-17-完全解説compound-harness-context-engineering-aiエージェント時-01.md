---
id: "2026-03-17-完全解説compound-harness-context-engineering-aiエージェント時-01"
title: "【完全解説】Compound / Harness / Context Engineering - AIエージェント時代の3大開発手法を徹底比較"
url: "https://qiita.com/emi_ndk/items/e86ce7def46f440385f9"
source: "qiita"
category: "ai-workflow"
tags: ["OpenAI", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

**「AIにコードを書かせているが、品質がバラバラで本番に出せない」**

2026年、この悩みを抱えるチームが爆発的に増えている。AIエージェントがコードを書く時代になったが、**エージェントを「管理する技術」が追いついていない**のだ。

この問題に対して、3つの革新的な開発手法が登場した：

1. **Compound Engineering** — Every社が提唱。「作業が蓄積するほど次の作業が楽になる」
2. **Harness Engineering** — OpenAIが提唱。「100万行をゼロ人間コードで書いた」方法論
3. **Context Engineering** — Anthropic/Martin Fowlerが体系化。「モデルが見る世界を設計する」

結論から言うと、**この3つは競合ではなく補完関係にある**。この記事で全貌を解説する。

## なぜ今、新しい開発手法が必要なのか

従来のソフトウェア開発はこうだった：

```
人間がコードを書く → 人間がレビューする → 人間がデプロイする
```

2026年のAIエージェント開発はこうなった
