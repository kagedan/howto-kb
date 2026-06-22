---
id: "2026-06-21-claude-opus-47入門-swe-bench-876375mp-visionapiマイグレー-01"
title: "Claude Opus 4.7入門 — SWE-bench 87.6%・3.75MP Vision・APIマイグレーションガイド"
url: "https://zenn.dev/kai_kou/articles/238-claude-opus-47-release-api-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "Gemini", "GPT"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

> 📌 **2026-06-19 追記**: 本記事は Claude Opus 4.7 リリース時点の情報です。現在は後継の **Claude Opus 4.8** が公開されています。最新モデルを検討する場合は Opus 4.8 の情報もあわせて確認してください。本記事は 4.7 世代の仕様・移行手順のリファレンスとして残しています。

## はじめに

2026年4月16日、AnthropicはフラッグシップモデルのアップグレードとなるClaude Opus 4.7を正式リリースしました。

この記事では、公式ドキュメントと公開情報をもとに、Claude Opus 4.7の主要な改善点・新機能・API移行ガイドを解説します。

### この記事で学べること

* Claude Opus 4.7のベンチマーク結果と旧モデルとの比較
* 高解像度Vision・xhigh努力レベル・タスクバジェットの詳細
* Opus 4.6からの移行で対応が必要な5つの破壊的変更
* 移行コードサンプル（Python）

### 対象読者

* Claude APIを利用している開発者
* Claude Opus 4.6をプロダクションで運用している方
* AIエージェント開発に関心があるエンジニア

---

## TL;DR

* **価格変更なし**: $5/$25 per million tokens（Opus 4.6と同一）
* **SWE-bench Verified 87.6%**: 4.6比+6.8ポイント、GPT-5.4(57.7%)・Gemini 3.1 Pro(80.6%)を上回る
* **Vision 98.5%**: 視覚精度ベンチマークで4.6比+44ポイント
* **破壊的変更あり**: `thinking: {type: "enabled"}` と `temperature/top_p/top_k` が400エラーに

---

## Claude Opus 4.7 の概要

Claude Opus 4.7は、Anthropicの一般公開モデルの中で最も高性能なモデルです。モデルIDは `claude-opus-4-7` で、Claude API・Amazon Bedrock（研究プレビュー）・Google Cloud Vertex AI・Microsoft Foundryで利用できます。

なお、Claude Sonnet 4（`claude-sonnet-4-20250514`）とClaude Opus 4（`claude-opus-4-20250514`）は2026年4月14日付で非推奨が発表されており、2026年6月15日に廃止予定です。

---

## ベンチマーク

### コーディング

| ベンチマーク | Opus 4.6 | Opus 4.7 | 改善 |
| --- | --- | --- | --- |
| SWE-bench Verified | 80.8% | **87.6%** | +6.8pt |
| SWE-Bench Pro | 53.4% | **64.3%** | +10.9pt |
| 本番タスク解決数 | 基準 | **3x** | +200% |

SWE-bench Verifiedはソフトウェアエンジニアリングの実タスクを評価するベンチマークです。87.6%という数値はGemini 3.1 Pro（80.6%）・GPT-5.4（57.7%）を上回ります。

SWE-Bench Proは多言語対応の難易度の高いバリアントです。64.3%はGPT-5.4（57.7%）・Gemini 3.1 Pro（54.2%）より高い水準です。

### Vision（視覚認識）

| ベンチマーク | Opus 4.6 | Opus 4.7 |
| --- | --- | --- |
| Visual-acuity benchmark | 54.5% | **98.5%** |

高解像度サポートにより、視覚精度ベンチマークで約44ポイントの大幅改善を達成しています。

### その他

* **Finance Agent評価**: 最高水準（State-of-the-art）
* **OfficeQA Pro**: エラー率21%削減

---

## 主要な新機能

### 1. 高解像度Vision（3.75MP）

Claude Opus 4.7では、画像の最大入力解像度が大幅に向上しています。

| 仕様 | Opus 4.6以前 | Opus 4.7 |
| --- | --- | --- |
| 最大解像度（長辺） | 1,568 px | **2,576 px** |
| 最大ピクセル数 | 約1.15 MP | **約3.75 MP** |
| 最大画像トークン | 約1,600 tokens/枚 | **約4,784 tokens/枚** |
| 座標の返却 | スケール変換が必要 | **実ピクセルと1:1対応** |

高解像度サポートは自動的に有効です。ベータヘッダーや追加設定は不要です。

**注意点**: 画像1枚あたりのトークン消費が最大3倍になります。コスト見積もりの再計算が必要です。高解像度が不要な場合は、画像をダウンサンプリングして送信することでコストを抑えられます。

コンピューターユース（computer use）のスクリーンショット解析や文書分析など、視覚精度が重要なワークフローで特に効果的です。

### 2. xhigh 努力レベル

Opus 4.7では、`effort` パラメータに新しいレベル `"xhigh"` が追加されました。

```
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "xhigh"},  # 新しいレベル
    messages=[{"role": "user", "content": "複雑なコーディングタスク..."}],
)
```

各努力レベルの使い分けガイド:

| レベル | 推奨用途 |
| --- | --- |
| `"max"` | 最高水準の精度が必要な場面（コスト増・稀に過剰思考） |
| `"xhigh"` ★新 | **コーディング・エージェントユースケースに最適** |
| `"high"` | 知的精度が求められる大半のユースケース（最低推奨） |
| `"medium"` | コスト重視・精度のトレードオフが許容できる場合 |
| `"low"` | 短いタスク・レイテンシ優先・非推論的なワークフロー |

### 3. タスクバジェット（パブリックベータ）

`task_budget` パラメータがパブリックベータとして追加されました。長時間のエージェント処理でトークン消費をガイドできます。

```
client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=64000,
    output_config={
        "task_budget": {"type": "tokens", "total": 50000},
    },
    messages=[...],
    betas=["task-budgets-2026-03-13"],
)
```

### 4. 新トークナイザー

Opus 4.7では新しいトークナイザーが採用されています。同一テキストに対して、Opus 4.6と比較して **1.0〜1.35倍のトークン数**（最大35%増）になります。

```
# Token counting APIが返す値が変わる
response = client.messages.count_tokens(
    model="claude-opus-4-7",  # 4.6とは異なる値が返る
    messages=[{"role": "user", "content": "..."}],
)
```

`max_tokens` の設定に余裕を持たせること、コンパクション（compaction）のトリガーも再確認することが推奨されています。

---

## APIマイグレーションガイド

Opus 4.7にはOpus 4.6からの **5つの破壊的変更** があります。移行前に必ず対応してください。

### 破壊的変更1: Extended thinking の廃止

**旧API（Opus 4.6）**:

```
# ❌ Opus 4.7では400エラー
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "enabled", "budget_tokens": 32000},
    messages=[...],
)
```

**新API（Opus 4.7）**:

```
# ✅ adaptive thinking + effort に移行
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "xhigh"},
    messages=[...],
)
```

adaptive thinkingはデフォルトで **無効** です。思考を有効にするには `thinking: {type: "adaptive"}` を明示的に指定してください。

### 破壊的変更2: サンプリングパラメータの削除

```
# ❌ Opus 4.7では400エラー
client.messages.create(
    model="claude-opus-4-7",
    temperature=0.7,  # 削除
    top_p=0.9,        # 削除
    top_k=40,         # 削除
    messages=[...],
)

# ✅ これらのパラメータを完全に省略する
client.messages.create(
    model="claude-opus-4-7",
    messages=[...],
)
```

`temperature=0` による決定的な出力は、以前のモデルでも完全な再現性を保証していませんでした。Opus 4.7では代わりにプロンプトで挙動を制御します。

### 破壊的変更3: Thinking content のデフォルト変更

Opus 4.7では、思考ブロック（thinking blocks）の `thinking` フィールドがデフォルトで空（`"omitted"`）になります。

```
# ✅ 思考内容を表示したい場合は display を明示
thinking = {
    "type": "adaptive",
    "display": "summarized",  # "omitted"(デフォルト) or "summarized"
}
```

プロダクトでユーザーに推論過程を見せている場合、Opus 4.7では思考開始前に長い無音期間が生じます。`display: "summarized"` を設定して可視化してください。

### 破壊的変更4: トークナイザー変更

同じテキストでトークン数が変わります。コスト計算・レート制限・バジェット管理のロジックを見直してください。

```
# ✅ max_tokens に余裕を持たせる
client.messages.create(
    model="claude-opus-4-7",
    max_tokens=100000,  # 4.6より多めに設定
    messages=[...],
)
```

### 破壊的変更5: Prefill の削除（4.6から引き継ぎ）

```
# ❌ Opus 4.7では400エラー
client.messages.create(
    model="claude-opus-4-7",
    messages=[
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "```json\n"},  # prefill 不可
    ],
)

# ✅ structured outputs または system prompt で代替
client.messages.create(
    model="claude-opus-4-7",
    system="必ずJSON形式で回答してください。",
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {"result": {"type": "string"}},
                "required": ["result"],
                "additionalProperties": False,
            },
        }
    },
    messages=[{"role": "user", "content": "..."}],
)
```

---

## Claude Codeの新機能

Claude Opus 4.7とあわせて、Claude Codeにも新機能が追加されました。

### `/ultrareview` コマンド

専用のコードレビューセッションを開始するコマンドです。`xhigh` 努力レベルで徹底的なレビューを実行します。

### Claude API スキルによる自動移行

Claude Codeでは、Opus 4.7への移行を自動化するコマンドが利用できます。

```
/claude-api migrate this project to claude-opus-4-7
```

このスキルはモデルIDの置換・破壊的パラメータ変更・effort設定の適用をコードベース全体に自動適用し、手動確認チェックリストを出力します。

---

## 行動上の変更点（破壊的変更ではないが注意が必要）

API変更ではありませんが、プロンプトの調整が必要になる可能性があります。

| 変更点 | Opus 4.6 | Opus 4.7 |
| --- | --- | --- |
| 応答の長さ | 固定的な詳細度 | タスク複雑度に応じて動的に変化 |
| 指示の解釈 | 多少の推定を行う | **より逐語的に解釈** |
| 文体 | 温かみのあるトーン | **より直接的・簡潔** |
| サブエージェント | デフォルトで多め | デフォルトで少なめ（プロンプトで制御可） |
| ツール使用 | 積極的 | 少なめ（reasoningを優先） |
| 努力レベル遵守 | 緩め | **厳格**（低努力では意図的に範囲を絞る） |

---

## 移行チェックリスト

移行時に確認すべき項目をまとめます。

---

## まとめ

Claude Opus 4.7の主要なポイントをまとめます。

* **コーディング性能が大幅向上**: SWE-bench Verified 87.6%はGPT-5.4・Gemini 3.1 Proを上回る
* **Visionが実用水準に**: 3.75MP高解像度対応・視覚精度98.5%
* **新しい努力レベルxhigh**: エージェント・コーディング用途の最適解
* **価格据え置き**: $5/$25 per MTokで上位モデルへアップグレード可能
* **移行時は5つの破壊的変更に注意**: 特に `thinking` パラメータと sampling params

Claude Code の `/claude-api migrate` コマンドを活用することで、破壊的変更への対応を自動化できます。

## 参考リンク
