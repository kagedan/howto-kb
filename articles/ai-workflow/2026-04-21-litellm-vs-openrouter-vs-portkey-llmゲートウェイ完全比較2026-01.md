---
id: "2026-04-21-litellm-vs-openrouter-vs-portkey-llmゲートウェイ完全比較2026-01"
title: "LiteLLM vs OpenRouter vs Portkey: LLMゲートウェイ完全比較【2026年版】"
url: "https://zenn.dev/agdexai/articles/llm-gateway-comparison-2026"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

# LiteLLM vs OpenRouter vs Portkey: LLMゲートウェイ完全比較【2026年版】

AIエージェント開発において、**LLMゲートウェイ**は欠かせない存在になりました。複数のLLMプロバイダーを統一的に扱い、コスト最適化・フォールバック・レート制限を自動管理する—これがLLMゲートウェイの役割です。

本記事では2026年に注目すべき3大ゲートウェイ「**LiteLLM**」「**OpenRouter**」「**Portkey**」を徹底比較します。

---

## なぜLLMゲートウェイが必要か？

AIエージェントを本番環境で運用すると、こんな課題に直面します：

* **プロバイダーロックイン**：OpenAIに依存しすぎると、障害時に詰む
* **コスト爆発**：GPT-4oを常に使うと費用がかさむ
* **レート制限**：スパイク時にリクエストが詰まる
* **可観測性の欠如**：どのモデルに何トークン使ったか把握しにくい

LLMゲートウェイはこれらをまとめて解決します。

---

## 3ツール概要

### LiteLLM

* **URL**: <https://litellm.ai>
* **タイプ**: オープンソース（セルフホスト or クラウド）
* **対応モデル**: 100以上（OpenAI / Anthropic / Gemini / Mistral / Ollama など）
* **特徴**: OpenAI互換API、ロードバランシング、フォールバック、コスト追跡

### OpenRouter

### Portkey

---

## 機能比較表

| 機能 | LiteLLM | OpenRouter | Portkey |
| --- | --- | --- | --- |
| 対応モデル数 | 100+ | 300+ | 250+ |
| セルフホスト | ✅ | ❌ | ✅（一部） |
| フォールバック | ✅ | ✅ | ✅ |
| ロードバランシング | ✅ | ✅ | ✅ |
| コスト追跡 | ✅ | ✅ | ✅ |
| プロンプト管理 | △ | ❌ | ✅ |
| ガードレール | △ | ❌ | ✅ |
| 無料枠 | OSS無料 | ✅ | ✅（制限あり） |
| OpenAI互換 | ✅ | ✅ | ✅ |

---

## 深掘り比較

### 1. LiteLLM — セルフホスト派の王道

```
import litellm

# 100+モデルを同じインターフェースで呼び出す
response = litellm.completion(
    model="anthropic/claude-3-5-sonnet",
    messages=[{"role": "user", "content": "Hello!"}]
)

# フォールバック設定
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
    fallbacks=["claude-3-5-sonnet", "gemini/gemini-1.5-pro"]
)
```

**強み：**

* 完全オープンソース、データが外部に出ない
* プロキシサーバーとして起動でき、既存コードを変更不要
* Kubernetes環境との親和性が高い

**弱み：**

* セルフホストの運用コストがかかる
* UIが比較的シンプル

**向いている人：** セキュリティ重視・社内インフラ統一・エンタープライズ

---

### 2. OpenRouter — モデル探索と実験に最強

```
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-openrouter-key",
)

# 300+モデルを1つのAPIで
response = client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

**強み：**

* 無料モデルが多数（Llama 3 / Mistral / Gemma など）
* 自動的にコスト最安ルーティング
* モデル探索・プロトタイプに最適

**弱み：**

* クラウド経由のためデータプライバシーに注意
* 本番環境の細かい制御が難しい

**向いている人：** スタートアップ・個人開発者・モデル比較実験

---

### 3. Portkey — 本番運用の可観測性特化

```
from portkey_ai import Portkey

portkey = Portkey(
    api_key="your-portkey-key",
    virtual_key="openai-virtual-key"
)

# プロダクション向け：ログ・トレース・ガードレール自動適用
response = portkey.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

**強み：**

* 詳細なトレース・ログ・コスト分析ダッシュボード
* プロンプトのバージョン管理
* A/Bテストがネイティブサポート

**弱み：**

* 高度な機能は有料プラン必須
* セットアップがやや複雑

**向いている人：** プロダクションチーム・MLOps・コスト管理重視

---

## ユースケース別おすすめ

### 🔬 実験・プロトタイプ段階

→ **OpenRouter** 一択。無料モデルで費用ゼロ、セットアップ5分。

### 🏢 社内・エンタープライズ環境

→ **LiteLLM** のセルフホスト。データが外に出ない、既存インフラに統合しやすい。

### 🚀 プロダクション運用・チーム開発

→ **Portkey**。可観測性・プロンプト管理・A/Bテストが揃っている。

### 💰 コスト最適化最優先

→ **OpenRouter**（自動ルーティング）+ **LiteLLM**（フォールバック制御）の組み合わせも有効。

---

## 2026年のトレンド：ゲートウェイの役割拡大

LLMゲートウェイは単なる「プロキシ」から進化しています：

1. **エージェント対応**：Tool calling / Function calling の標準化
2. **セマンティックキャッシュ**：同意の質問を検出してAPI節約
3. **ガードレール統合**：有害コンテンツ・PII漏洩を自動ブロック
4. **マルチモーダル対応**：画像・音声・動画も統一インターフェース

---

## まとめ

| ゲートウェイ | 最適シーン |
| --- | --- |
| **LiteLLM** | セルフホスト・エンタープライズ・インフラ統合 |
| **OpenRouter** | 実験・スタートアップ・無料モデル活用 |
| **Portkey** | プロダクション・可観測性・チーム開発 |

3つを排他的に選ぶ必要はなく、\*\*OpenRouter（実験）→ LiteLLM（本番セルフホスト）→ Portkey（可観測性レイヤー）\*\*という組み合わせも現実的です。

AIエージェントの最新ツールは **[AgDex.ai](https://agdex.ai)** で。360以上のツールを4言語で収録中。

---

*関連記事：*
