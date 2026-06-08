---
id: "2026-06-08-月3万pvの教育サイトを1人で運営する私がchatgptclaude-codegeminigrokを-01"
title: "月3万PVの教育サイトを1人で運営する私が、ChatGPT・Claude Code・Gemini・Grokを役割分担している理由"
url: "https://qiita.com/checkmerun/items/05b265e038d18a53f524"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "LLM", "Gemini", "GPT", "qiita"]
date_published: "2026-06-08"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## 個人開発で4種のLLMを役割分担した話——ChatGPT・Claude Code・Grok・Gemini

個人開発サービス [CheckMe](https://checkme.run) を1人で運営しながら、LLMを役割分担して使うようになった記録。

### 使い分けの整理

| LLM | 役割 | 具体的な業務 |
| --- | --- | --- |
| ChatGPT | 壁打ち・要件整理 | Claude Codeへの仕様書作成 |
| Claude Code | 実装 | main.py編集・テンプレート作成・デプロイ |
| Grok | SNS・リサーチ | 競合分析・ネット文化理解 |
| Gemini | 発想・企画 | ユーザーヒアリング・アイデア出し |

### Claude Codeへの依頼品質を上げる方法

直接Claude Codeに「〇〇を実装して」と伝えるより、**先にChatGPTで要件を整理してから渡す**方が精度が上がる。

```
ChatGPT（要件整理）→ Claude Code（実装）
```

このフローを意識するようになってから、手戻りが減った。

### Geminiのユーザーヒアリング活用

「非通塾層の中学生6ケースを深掘りインタビューして」とGeminiに依頼すると、UXリサーチャー・教育アナリスト・元受験生などのロールを担って20往復以上の会話を再現してくれる。

これをCLAUDE.mdとDBに記録して、実装の判断材料にしている。

### まとめ

「どのLLMが最強か」より「誰に何を頼むか」で考えた方が成果が出る。

#個人開発 #Claude #ChatGPT #Gemini #LLM #AI活用
