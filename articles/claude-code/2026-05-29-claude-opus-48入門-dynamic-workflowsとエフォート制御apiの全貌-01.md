---
id: "2026-05-29-claude-opus-48入門-dynamic-workflowsとエフォート制御apiの全貌-01"
title: "Claude Opus 4.8入門 — Dynamic Workflowsとエフォート制御APIの全貌"
url: "https://qiita.com/kai_kou/items/70cdb50e3abe6fe775f2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "Gemini", "GPT"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

![Claude Opus 4.8 — Dynamic Workflowsと並列エージェントのヒーローイラスト](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-opus-48-dynamic-workflows-api-guide/01-hero.png)

## はじめに

2026年5月28日、Anthropicが**Claude Opus 4.8**（APIモデルID: `claude-opus-4-8`）をリリースしました。Opus 4.7から41日という短サイクルのアップデートで、SWE-bench Proで**69.2%**を達成（Opus 4.7比+4.9%）し、コーディングAIの最高スコアを更新しています。

公式ドキュメントをもとに、Claude Opus 4.8の主要変更点・ベンチマーク・API実装方法を解説します。

### この記事で学べること

- Claude Opus 4.8の主要ベンチマークとOpus 4.7との差分
- **Dynamic Workflows**の仕組みと活用シナリオ
- **エフォート制御**（`output_config: {effort: ...}`）の正確なAPI実装
- Adaptive ThinkingとEffortを組み合わせた最適化パターン
- 料金・コスト最適化のポイント

### 対象読者

- Anthropic APIを利用しているエンジニア
- Claude Codeを業務で活用している開発者
- AIエージェント構築のコスト最適化を検討している方

### 前提環境

- Python 3.11以上
- `anthropic` パッケージ最新版（`pip install -U anthropic`）

## TL;DR

- **SWE-bench Pro: 69.2%**（Opus 4.7比+4.9%）でコーディングAI最高スコアを更新
- **Dynamic Workflows**（リサーチプレビュー）: 数百の並列サブエージェントを単一セッションで協調実行
- **エフォート制御**: `output_config={"effort": "xhigh"}` のような形式で5段階（`low`〜`max`）を制御
- **Adaptive Thinking**: `thinking: {type: "adaptive"}` を指定すると複雑度に応じて自動で思考量を調整
- **Fast mode**: 最大2.5倍速・前世代比3倍コストダウン（$10/M in / $50/M out）
- 料金はOpus 4.7から**据え置き**（$5/M input、$25/M output）

![Dynamic Workflows アーキテクチャ図 — オーケストレーターと並列サブエージェントの構成](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-opus-48-dynamic-workflows-api-guide/02-dynamic-workflows-architecture.png)

## Claude Opus 4.8 概要

### リリース情報

| 項目 | 内容 |
|------|------|
| APIモデルID | `claude-opus-4-8` |
| リリース日 | 2026年5月28日 |
| コンテキスト窓 | 1,000,000トークン |
| 利用可能プラットフォーム | Claude.ai / Anthropic API / Amazon Bedrock / Google Vertex AI / Microsoft Foundry / GitHub Copilot |

### 主な改善点

Anthropicの[公式発表](https://www.anthropic.com/news/claude-opus-4-8)によると、Opus 4.8は3つの観点で進化しています。

1. **コーディング精度**: コード欠陥を見逃す頻度がOpus 4.7比で**4倍低減**
2. **アジェンティック信頼性**: 不確実な分析結果を自ら積極的にフラグ立て
3. **大規模並列実行**: Dynamic Workflowsで数百のサブエージェントを協調実行

## ベンチマーク比較

[computingforgeeks.com](https://computingforgeeks.com/claude-opus-4-8-released-features-benchmarks/)が集計した公開ベンチマークです。

| ベンチマーク | Opus 4.8 | Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|-------------|----------|----------|---------|----------------|
| SWE-bench Pro（コーディング） | **69.2%** | 64.3% | 58.6% | 54.2% |
| Terminal-Bench 2.1 | 74.6% | 66.1% | **78.2%** | 70.3% |
| OSWorld-Verified（コンピュータ操作） | **83.4%** | 82.8% | 78.7% | 76.2% |
| GDPval-AA（知識労働） | **1890** | 1753 | 1769 | 1314 |
| Finance Agent v2 | **53.9%** | 51.5% | 51.8% | 43.0% |
| HLE with tools（多分野推論） | **57.9%** | 54.7% | 52.2% | 51.4% |

コーディング（SWE-bench Pro: +4.9%）と知識労働（GDPval-AA: +137ポイント）で大きな向上が見られます。Terminal-Bench 2.1のみGPT-5.5がリードを維持していますが、他の主要ベンチマークではOpus 4.8が首位です。

## Dynamic Workflows（新機能）

### 概要

Dynamic Workflowsは、Claude Code + Opus 4.8を組み合わせた**大規模コーディング自動化機能**です。単一セッション内で数百の並列サブエージェントを協調させ、コードベース全体の移行やセキュリティ監査を自律実行できます。

Anthropicの[公式発表](https://www.anthropic.com/news/claude-opus-4-8)では、次のユースケースが挙げられています。

- **フレームワーク移行**: 数十万行規模のコードベースを並列処理でデプロイまで完結
- **並列テスト**: 複数モジュールのテストスイートを同時実行・自動修正
- **セキュリティ監査**: 全コードベースを分割してサブエージェントが横断チェック

### 利用条件

現時点（2026年5月）では**リサーチプレビュー**段階です。


> **利用可能プラン**: Claude Code **Enterprise / Team / Max** プランのみ  
> 個人のProプランでは利用できません。


一般提供の開始時期は[Anthropic公式リリースノート](https://www.anthropic.com/news/claude-opus-4-8)でご確認ください。

## エフォート制御（Effort Control）

Anthropicの[公式ドキュメント](https://platform.claude.com/docs/en/build-with-claude/effort)によると、Opus 4.8では`output_config`パラメータ内の`effort`でトークン使用量と応答品質のトレードオフを制御できます。

### エフォートレベル一覧

| レベル | 特徴 | 推奨ユースケース |
|--------|------|----------------|
| `low` | 最小トークン消費 | 分類・簡単なQ&A・高頻度サブエージェント |
| `medium` | バランス型 | コスト重視のエージェントタスク |
| `high` | **デフォルト** | 複雑な推論・一般的なコーディング |
| `xhigh` | 拡張推論 | コーディング・長時間エージェントタスク（**推奨開始点**） |
| `max` | 最大思考量 | フロンティア水準の問題のみ |

公式ドキュメントでは「コーディングとエージェントタスクは`xhigh`から始め、品質評価後に`high`へ下げる」ことが推奨されています。

### Python実装例

#### 基本的なエフォート制御

```python
import anthropic

client = anthropic.Anthropic()

# コーディングタスク: xhigh推奨、max_tokens大きめに設定
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=64000,  # xhigh/maxでは64k以上を推奨
    messages=[
        {
            "role": "user",
            "content": "このPythonコードのバグを全て特定し修正してください:\n\ndef divide(a, b):\n    return a / b\n\ndef batch_process(items):\n    results = []\n    for item in items:\n        results.append(divide(item['value'], item['divisor']))\n    return results"
        }
    ],
    output_config={"effort": "xhigh"},
)

print(response.content[0].text)
```

#### コスト最適化: 用途別エフォート切り替え

```python
import anthropic

client = anthropic.Anthropic()

def ask_claude(question: str, task_type: str = "general") -> str:
    # タスク種別ごとにエフォートを動的に切り替え
    effort_map = {
        "simple":  "low",    # 分類・簡単なQ&A
        "general": "high",   # 一般的なタスク（デフォルト）
        "coding":  "xhigh",  # コーディング・デバッグ
        "frontier": "max",   # 最高品質が必要なケース
    }
    effort = effort_map.get(task_type, "high")

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        messages=[{"role": "user", "content": question}],
        output_config={"effort": effort},
    )
    return response.content[0].text


# 使用例
summary = ask_claude("この文章を1行で要約: ...", task_type="simple")
review  = ask_claude("このコードのセキュリティ問題を全て洗い出せ", task_type="coding")
```


> **注意**: `effort` パラメータは `output_config` の中に指定します。`thinking` 内に入れると動作しません。


## Adaptive Thinking との組み合わせ

Claude Opus 4.8では、**手動での `budget_tokens` 指定（`thinking: {type: "enabled", budget_tokens: N}`）は非サポート**（400エラー）です。代わりに `thinking: {type: "adaptive"}` を使用します。

公式ドキュメントによると、`high` / `xhigh` / `max` エフォートではほぼ常に深く思考し、`low` / `medium` では問題の複雑度に応じて思考をスキップします。

```python
import anthropic

client = anthropic.Anthropic()

# Adaptive Thinking + エフォート制御の組み合わせ
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=32000,
    thinking={
        "type": "adaptive"  # 複雑度に応じて自動で思考量を調整
    },
    messages=[
        {
            "role": "user",
            "content": "マイクロサービスとモノリシックアーキテクチャのトレードオフを詳細に分析してください"
        }
    ],
    output_config={"effort": "high"},
)

# 思考ブロックとテキストブロックが両方含まれる可能性
for block in response.content:
    if block.type == "thinking":
        print(f"[Thinking]: {block.thinking[:100]}...")
    elif block.type == "text":
        print(block.text)
```

![エフォートレベル比較図 — low〜maxの5段階でトークン消費と品質のトレードオフを可視化](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-opus-48-dynamic-workflows-api-guide/03-effort-levels.png)

## 料金とコスト最適化

### 標準料金（Opus 4.7から据え置き）

| モード | 入力 | 出力 |
|--------|------|------|
| 標準 | $5 / 1M tokens | $25 / 1M tokens |
| Fast mode（最大2.5倍速） | $10 / 1M tokens | $50 / 1M tokens |

[Anthropic公式料金ページ](https://platform.claude.com/docs/en/about-claude/pricing)によると、Fast modeの実コストは**前世代比3倍低減**されています（Opus 4.7: $30/M in・$150/M out → Opus 4.8: $10/M in・$50/M out）。

### コスト最適化の4戦略

1. **プロンプトキャッシュ活用**: 繰り返しのシステムプロンプトをキャッシュして最大**90%コスト削減**
2. **バッチ処理**: Message Batches APIで最大**50%コスト削減**
3. **エフォート動的制御**: 単純タスクは`low`、コーディングは`xhigh`と使い分け
4. **US-only推論**: データ残留要件がある場合のみ1.1倍の追加料金

#### プロンプトキャッシュとの組み合わせ例

```python
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """あなたはシニアソフトウェアエンジニアです。
コードのセキュリティ、可読性、パフォーマンスを重点的にレビューしてください。
[以下、長大なコーディング規約...（数千トークン規模）]
"""

# キャッシュ可能なシステムプロンプト + xhigh エフォート
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    system=[
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},  # キャッシュ有効化
        }
    ],
    messages=[
        {"role": "user", "content": "このPRのコードをレビューしてください: ..."}
    ],
    output_config={"effort": "xhigh"},
)

print(response.content[0].text)
# cache_read_input_tokensが増えると料金が大幅に削減される
print(f"キャッシュヒット: {response.usage.cache_read_input_tokens} tokens")
```

## 注意点

### Dynamic Workflowsの利用制限

現時点でDynamic WorkflowsはClaude Code **Enterprise/Team/Max**プランに限定されています。個人のProプランでは利用できません。一般提供の開始時期は[公式リリースノート](https://www.anthropic.com/news/claude-opus-4-8)をご確認ください。

### xhigh/maxでのmax_tokens設定

公式ドキュメントの推奨事項として、`xhigh`または`max`エフォートでは**`max_tokens=64000`以上**を設定してください。サブエージェントの並列実行やツール呼び出しが多くなるため、トークン不足で途中終了するリスクがあります。

### budget_tokensは非サポート

Opus 4.8では `thinking: {type: "enabled", budget_tokens: N}` を指定すると**400エラー**が返ります。Adaptive Thinking（`thinking: {type: "adaptive"}`）と`effort`パラメータを組み合わせた方法に移行してください。

### モデル移行

既存のOpus 4.7コード（`claude-opus-4-7`）からの移行は、モデルIDの変更のみで対応可能です。`effort`パラメータを省略するとデフォルト値（`high`）が適用されます。Opus 4.7で`budget_tokens`を使用していた場合は、`thinking: {type: "adaptive"}`と`effort`の組み合わせに切り替えてください。

## まとめ

- **Claude Opus 4.8**（`claude-opus-4-8`）は2026年5月28日リリース。SWE-bench Pro 69.2%でコーディングAI最高スコアを達成
- **Dynamic Workflows**（リサーチプレビュー）で数百の並列サブエージェントを協調実行可能に。大規模コードベース移行が現実的な選択肢に
- **エフォート制御**は `output_config={"effort": "xhigh"}` の形式で指定。コーディングタスクは`xhigh`が推奨開始点
- **Adaptive Thinking** は `thinking: {type: "adaptive"}` を使用。手動`budget_tokens`はOpus 4.8では400エラーになるため移行が必要
- 料金はOpus 4.7から据え置き。Fast modeは前世代比3倍コストダウン。キャッシュとバッチの活用で大幅なコスト最適化が可能

## 参考リンク

- [Introducing Claude Opus 4.8 — Anthropic](https://www.anthropic.com/news/claude-opus-4-8)
- [Claude Opus 4.8 — anthropic.com](https://www.anthropic.com/claude/opus)
- [Effort — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Anthropic releases Opus 4.8 with new 'dynamic workflow' tool — TechCrunch](https://techcrunch.com/2026/05/28/anthropic-releases-opus-4-8-with-new-dynamic-workflow-tool/)
- [Claude Opus 4.8: Features, Benchmarks — ComputingForGeeks](https://computingforgeeks.com/claude-opus-4-8-released-features-benchmarks/)
- [Anthropic upgrades Claude with Opus 4.8 — 9to5Mac](https://9to5mac.com/2026/05/28/anthropic-upgrades-claude-with-new-opus-4-8-model-heres-whats-new/)
