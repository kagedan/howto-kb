---
id: "2026-04-11-gpt-54-thinking入門-reasoningeffortとosworld-v-75の推論a-01"
title: "GPT-5.4 Thinking入門 — reasoning.effortとOSWorld-V 75%の推論AIをAPI活用"
url: "https://zenn.dev/kai_kou/articles/189-gpt-54-thinking-reasoning-api-guide"
source: "zenn"
category: "cowork"
tags: ["API", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

OpenAIの**GPT-5.4 Thinking**は、2026年3月5日に発表された推論特化フラッグシップモデルです。従来のGPT-5.4（Computer Use / Tool Search 中心）とは異なり、**段階的な推論制御**と**最大1Mトークンのコンテキスト**を武器に、AIエージェントの自律タスク実行を大幅に強化しています。

特に注目すべきは、デスクトップ自動化ベンチマーク**OSWorld-Verified**で\*\*75.0%\*\*を達成し、人間ベースライン（72.4%）を超えたことです。これはGPT-5.2の47.3%から59%以上の改善であり、AIが実際の業務タスクをこなせるレベルに近づいていることを示します。

この記事では、エンジニアが押さえるべきGPT-5.4 Thinkingの仕組みと`reasoning.effort`パラメータの実装方法を解説します。

### この記事で学べること

* GPT-5.4 Thinkingと既存GPT-5.4の違い
* `reasoning.effort` パラメータの5段階制御と使い分け
* OSWorld-V・SWE-bench VerifiedなどのベンチマークとAIエージェントへの示唆
* 1Mトークンコンテキストの活用法と課金設計
* Python実装サンプル

### 対象読者

* OpenAI APIでエージェントを構築しているエンジニア
* 推論系LLMのコスト最適化を検討している方
* GPT-5.4の最新アップデートを把握したい方

### 前提環境

* Python 3.11+
* `openai` ライブラリ（最新版）
* OpenAI APIキー（GPT-5.4アクセス権限）

---

## TL;DR

* GPT-5.4 Thinkingは`reasoning.effort`（none/low/medium/high/xhigh）で推論深度を制御
* OSWorld-V 75.0%達成（人間72.4%超え）、SWE-bench Verified 57.7%
* 標準272Kトークン、実験的1Mトークン対応（長期エージェントタスクに有効）
* 料金: 入力$2.50/1Mトークン、出力$15.00/1Mトークン（272K超は割増）
* モデルラインナップ: Instant（GPT-5.3）/ Thinking（GPT-5.4）/ Pro（GPT-5.4 Pro）

---

## GPT-5.4 Thinkingとは

GPT-5.4 Thinkingは、OpenAIがGPT-5.3（Instant）とあわせて発表した推論フラッグシップモデルです。従来のGPT系列（汎用対話）とCodex系列（コード生成）を統合した単一モデルとして設計されており、[OpenAI公式アナウンス](https://openai.com/index/introducing-gpt-5-4/)によると「最もトークン効率の良い推論モデル」とされています。

### モデルラインナップの整理

2026年3月以降、ChatGPT/API のモデル選択は次の3ティアに整理されました：

| モデル名 | APIモデルID | コンテキスト | 用途 |
| --- | --- | --- | --- |
| Instant | `gpt-5.3` | 400Kトークン | 高速・汎用チャット |
| Thinking | `gpt-5.4` | 272K〜1Mトークン | 推論・エージェント |
| Pro | `gpt-5.4-pro` | 272K〜1Mトークン | 最高精度タスク |

さらに軽量版として`gpt-5.4-mini`（バランス型）・`gpt-5.4-nano`（超高速）も提供されています。

---

## ベンチマーク：人間を超えたデスクトップ自動化

GPT-5.4 Thinkingの最大の注目点は、実際のコンピュータ操作タスクにおける性能向上です。

### 主要ベンチマーク一覧

| ベンチマーク | GPT-5.4 Thinking | 参考値 | 意味 |
| --- | --- | --- | --- |
| **OSWorld-Verified** | **75.0%** | 人間72.4% | 実際のデスクトップ操作タスク |
| **SWE-bench Verified** | **57.7%** | — | ソフトウェアエンジニアリングタスク |
| **MMMU-Pro** | **81.2%** | GPT-5.2: 79.5% | マルチモーダル理解 |
| **GDPval** | **83%** | — | OpenAI内部の知識業務ベンチマーク |

**OSWorld-Verified**は、実際のPCデスクトップ操作（ファイル管理・ブラウザ操作・スプレッドシート編集など）の自律実行能力を測定するベンチマークです。GPT-5.4 ThinkingがGPT-5.2比で約59%改善し、人間ベースラインを超えたことは、AIエージェントが実業務タスクを代替できるレベルへの大きな一歩を示しています。

> We're excited to share that GPT-5.4 achieves 75.0% on OSWorld-Verified, surpassing the human baseline of 72.4% for the first time.  
> — [Introducing GPT-5.4 | OpenAI](https://openai.com/index/introducing-gpt-5-4/)（2026-03-05）

また、従来のGPT-5.2比で**虚偽の主張が1文あたり33%減少**、**レスポンス全体のエラーが18%減少**と、ファクチュアリティの改善も大きな特徴です。

---

## reasoning.effort パラメータ

GPT-5.4 Thinkingの核心機能が、`reasoning.effort` パラメータです。5段階でモデルの推論深度を制御でき、**速度・コスト・精度のトレードオフ**を開発者が細かく設定できます。

### 5段階のeffortレベル

| effortレベル | 相対コスト | 推奨ユースケース |
| --- | --- | --- |
| `none` | × 1.0 | ルックアップ、定型応答 |
| `low` | × 1.0（基準） | オートコンプリート、リアルタイムUI |
| `medium` | × 1.5〜2.0 | バランス型ワークロード |
| `high` | × 2.0〜3.0 | コードレビュー、文書分析バッチ |
| `xhigh` | × 3.0〜5.0 | セキュリティ監査、複雑プランニング |

### Python実装サンプル

```
from openai import OpenAI

client = OpenAI()

# reasoning.effortを指定してGPT-5.4 Thinkingを呼び出す
response = client.chat.completions.create(
    model="gpt-5.4",
    reasoning={
        "effort": "high"  # none / low / medium / high / xhigh
    },
    messages=[
        {
            "role": "user",
            "content": "以下のPythonコードのセキュリティ脆弱性を網羅的に列挙し、修正案を提示してください。\n\n```python\n# コードをここに記述\n```"
        }
    ]
)

print(response.choices[0].message.content)
```

### effortレベルの選び方

```
# ユースケース別の推奨設定

# 1. リアルタイムチャット（低レイテンシ優先）
effort_realtime = "low"

# 2. エージェントの計画フェーズ（精度と速度のバランス）
effort_planning = "medium"

# 3. コードレビュー・セキュリティチェック（精度優先）
effort_review = "high"

# 4. 長期エージェントタスクの最終判断（最高精度）
effort_critical = "xhigh"
```

---

## 1Mトークンコンテキストと料金設計

### コンテキストウィンドウ

GPT-5.4は272Kトークンのコンテキストウィンドウを標準とし、実験的APIでは最大1,050,000トークン（約1Mトークン）まで拡張可能です。

```
# 長期エージェントタスク用の設定例
# gpt-5.4 は実験的APIで最大1Mトークンのコンテキストをサポート
response = client.chat.completions.create(
    model="gpt-5.4",
    reasoning={"effort": "medium"},
    messages=[
        # 長いコンテキストを保持するエージェントワークフロー
        *conversation_history,
        {"role": "user", "content": user_input}
    ]
)
```

### 料金体系

[OpenAI API Pricing](https://developers.openai.com/api/docs/pricing)（2026年4月時点）によると：

| 料金区分 | 入力 | 出力 |
| --- | --- | --- |
| 標準（〜272Kトークン） | $2.50/1Mトークン | $15.00/1Mトークン |
| 長コンテキスト（272K超） | $5.00/1Mトークン | $22.50/1Mトークン |
| キャッシュ済み入力 | $0.25/1Mトークン | — |

**272Kトークンが料金の分岐点**です。コスト見積もりの際は、この閾値を超えるかどうかを事前に確認しましょう。

```
# コスト試算の例
def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """GPT-5.4の料金試算（USD）"""
    if input_tokens <= 272_000:
        input_cost = input_tokens * 2.50 / 1_000_000
    else:
        input_cost = input_tokens * 5.00 / 1_000_000
    
    if input_tokens <= 272_000:
        output_cost = output_tokens * 15.00 / 1_000_000
    else:
        output_cost = output_tokens * 22.50 / 1_000_000
    
    return input_cost + output_cost

# 例: 100Kトークン入力、10Kトークン出力
cost = estimate_cost(100_000, 10_000)
print(f"推定コスト: ${cost:.4f}")  # $0.4000
```

---

## エージェントワークフローへの応用

GPT-5.4 Thinkingは、長期エージェントタスクでの活用を主目的の一つとして設計されています。

### reasoning.effortを使ったエージェント設計

```
from openai import OpenAI
from typing import Literal

ReasoningEffort = Literal["none", "low", "medium", "high", "xhigh"]

class AgentWithReasoning:
    """reasoning.effortを使ったシンプルなエージェント実装"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.conversation_history = []
    
    def run(
        self,
        task: str,
        effort: ReasoningEffort = "medium"
    ) -> str:
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        
        response = self.client.chat.completions.create(
            model="gpt-5.4",
            reasoning={"effort": effort},
            messages=self.conversation_history
        )
        
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message

# 使用例
client = OpenAI()
agent = AgentWithReasoning(client)

# 計画フェーズ: medium effort
plan = agent.run(
    "Pythonでファイル監視システムを設計してください。要件：リアルタイム検知・ログ記録・アラート通知",
    effort="medium"
)

# 実装フェーズ: high effort（精度重視）
implementation = agent.run(
    "上記の設計に基づいて、production-readyなコードを実装してください",
    effort="high"
)

# セキュリティレビュー: xhigh effort
security_review = agent.run(
    "実装したコードのセキュリティ脆弱性を徹底的にレビューしてください",
    effort="xhigh"
)
```

### Computer Useとの組み合わせ

GPT-5.4はネイティブなComputer Use機能も備えており、ブラウザ操作やデスクトップ自動化と推論能力を組み合わせることができます。Computer Useの実装詳細については、[OpenAI公式ドキュメント（developers.openai.com）](https://developers.openai.com/api/docs/)のComputer Useガイドを参照してください。

---

## 注意点

### モデル選択の指針

```
タスク特性に応じたモデル選択:

リアルタイム応答が必要 → GPT-5.3 Instant
汎用推論・エージェント   → GPT-5.4 Thinking (medium effort)
高精度コード・分析       → GPT-5.4 Thinking (high effort)
最高精度・クリティカル   → GPT-5.4 Pro または xhigh effort
```

### コンテキスト長の管理

1Mトークンのコンテキストは強力ですが、272K超で料金が2倍になります。ほとんどのユースケースでは、**適切なチャンク分割とキャッシュ**を使うことでコストを抑えられます。

```
# キャッシュ活用のベストプラクティス
# システムプロンプトや共通コンテキストをセッション冒頭に配置すると
# キャッシュヒット率が向上し、入力コストを最大90%削減できる
messages = [
    {"role": "system", "content": system_prompt},  # キャッシュされやすい
    *dynamic_context,                                # 変動部分
    {"role": "user", "content": user_input}
]
```

---

## まとめ

* **GPT-5.4 Thinking**は推論特化フラッグシップ。`reasoning.effort`（5段階）でコスト・精度をコントロール
* \*\*OSWorld-V 75.0%\*\*達成で人間ベースライン（72.4%）超え。デスクトップ自動化エージェントで実業務代替が現実的に
* **272Kトークン**が標準コンテキスト。実験的1Mトークンは長期エージェントタスクに有効
* **料金の分岐点は272K**トークン。超過時は入力2倍・出力1.5倍に
* エージェント設計では「計画はmedium、実装はhigh、セキュリティレビューはxhigh」が基本指針

次のステップとして、Computer Use機能や長期エージェントタスクでの活用を検討する場合は[OpenAI Agents SDK](https://openai.com/index/openai-agents-sdk/)を参照することを推奨します。

---

## 参考リンク
