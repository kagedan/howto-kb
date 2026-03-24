---
id: "2026-03-23-ollama-018-claude-code-完全移行ガイド-v1ハックを卒業してネイティブapiで-01"
title: "Ollama 0.18 × Claude Code 完全移行ガイド ── 「/v1ハック」を卒業してネイティブAPIでローカルLLMを本物のエージェントにする【2026年3月最新】"
url: "https://qiita.com/AI-SKILL-LAB/items/6589c5124c391f923320"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "OpenAI", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# Ollama 0.18 × Claude Code 完全移行ガイド ── 「/v1ハック」を卒業してネイティブAPIでローカルLLMを本物のエージェントにする【2026年3月最新】

Claude Codeをローカルモデルで動かそうとしたことがある人なら、一度はこの壁に当たったことがあるかと思います。

「ツールが呼ばれない。ファイルを読んでくれない。Webを検索してくれない。テキストを返すだけで何も操作してくれない…」

実は、多くの場合これは **設定の問題ではなく、APIレベルの根本的な不一致** によるものです。Ollama の `/v1` (OpenAI互換モード) 経由での接続は、見かけ上は動いているように見えて、エージェントとしての核心機能を損なっています。

2026年3月14日にリリースされた **Ollama 0.18** は、この問題に正面から向き合いました。Claude Code のネイティブプロバイダーとして、`/api/chat` エンドポイントによる真の統合が実現したのです。

本記事では、その技術的な違いを整理しつつ、実際に動かすまでの手順と、見落と
