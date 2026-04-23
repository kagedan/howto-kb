---
id: "2026-04-10-claude-advisor-tool入門-sonnetとopusを組み合わせてコスト削減と品質向上-01"
title: "Claude Advisor Tool入門 — SonnetとOpusを組み合わせてコスト削減と品質向上を両立する"
url: "https://qiita.com/kai_kou/items/e7347356fee8084cfdaf"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

2026年4月9日、AnthropicはClaude APIに**Advisor Tool**（`advisor_20260301`）をパブリックベータとして追加しました。

このツールは、より高速・低コストな**Executorモデル**（SonnetやHaiku）と、より高知能な**Advisorモデル**（Opus 4.6）を1つのAPIリクエスト内で組み合わせる仕組みです。Executorがタスクを自律的に実行しながら、必要な場面だけOpusに戦略的なガイダンスを求めます。

**この記事で学べること：**

* Advisor Toolの仕組みとユースケース
* Python・TypeScriptでの実装方法
* SWE-benchで+2.7ppを達成したベンチマーク結果とコスト削減の内訳
* マルチターン会話・プロンプトキャッシュ・コスト制御の実践的なパターン

**対象読者：**

* Claude APIを使ってAIエージェントを構築しているエンジニア
* コスト削減と品質向上を同時に追求したい方
* Opus相当の品質をSonnetのコストで得たい方

---

## TL;DR

* **Advisor Tool** = Executor（Sonnet/Haiku）が実行し、必要なときだけAdvisor（Opus）が戦略指示
* **単一の `/v1/messages` 内で完結**。追加ラウンドトリップなし
* **Sonnet + Opus Advisor**: SWE-bench Multilingual +2.7pp、コスト -11.9%（Sonnet単独比）
* **Haiku + Opus Advisor**: BrowseComp 41.2%（Haiku単独 19.7% の2倍）、Sonnetより85%安
* ベータヘッダー: `anthropic-beta: advisor-tool-2026-03-01`

---

## Advisor Toolとは

従来のマルチエージェント設計では、大きなモデルが計画を立て、小さなモデルが実行するという「オーケストレーター → ワーカー」パターンが一般的でした。Advisor Toolはこのパターンを**逆転**させます。

> 小さなモデル（Sonnet/Haiku）がタスク全体を駆動し、行き詰まったときや重要な判断が必要なときだけ、大きなモデル（Opus）に相談する

Advisorは以下の特徴を持ちます：

| 特徴 | 内容 |
| --- | --- |
| ツール呼び出しなし | Advisorはツールを使えない。計画・方針のみを返す |
| ユーザー向け出力なし | Advisorの出力はExecutorへの内部ガイダンスのみ |
| 短い応答 | 典型的に400〜700 text tokens（thinking込みで1,400〜1,800 tokens） |
| サーバーサイド処理 | APIリクエストは1回のみ。クライアント側の追加実装不要 |

**適しているユースケース：**

* コーディングエージェント（複雑な実装タスク）
* Computer Use（マルチステップの画面操作）
* 長期研究パイプライン（複数ステップのリサーチ）

**向いていないケース：**

* 単発のQ&A（計画不要のシンプルな質問）
* ユーザーが自分でモデルを選ぶ純粋なモデルルーター
* 毎ターンAdvisorレベルの知能が必要なタスク

---

## モデルの互換性

現在サポートされている組み合わせは以下のとおりです：

| Executor（実行モデル） | Advisor（助言モデル） |
| --- | --- |
| `claude-haiku-4-5-20251001` | `claude-opus-4-6` |
| `claude-sonnet-4-6` | `claude-opus-4-6` |
| `claude-opus-4-6` | `claude-opus-4-6` |

**ルール：** AdvisorはExecutorと同等以上の能力を持つモデルでなければなりません。サポートされていないペアを指定した場合、APIは `400 invalid_request_error` を返します。

---

## クイックスタート（Python）

最小構成の実装例です。`tools` 配列にAdvisorツールを追加するだけで有効になります。

```
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-sonnet-4-6",      # Executor
    max_tokens=4096,
    betas=["advisor-tool-2026-03-01"],
    tools=[
        {
            "type": "advisor_20260301",
            "name": "advisor",
            "model": "claude-opus-4-6",  # Advisor
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Goでグレースフルシャットダウン付きの並行ワーカープールを実装してください。",
        }
    ],
)

print(response)
```

`betas=["advisor-tool-2026-03-01"]` を追加すれば、既存のAPIコードに数行加えるだけで有効化できます。

### cURLでの実行

```
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "anthropic-beta: advisor-tool-2026-03-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-sonnet-4-6",
        "max_tokens": 4096,
        "tools": [
            {
                "type": "advisor_20260301",
                "name": "advisor",
                "model": "claude-opus-4-6"
            }
        ],
        "messages": [{
            "role": "user",
            "content": "Goでグレースフルシャットダウン付きの並行ワーカープールを実装してください。"
        }]
    }'
```

---

## TypeScript実装

```
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

async function main() {
  const response = await client.beta.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 4096,
    betas: ["advisor-tool-2026-03-01"],
    tools: [
      {
        type: "advisor_20260301",
        name: "advisor",
        model: "claude-opus-4-6",
      },
    ],
    messages: [
      {
        role: "user",
        content:
          "Goでグレースフルシャットダウン付きの並行ワーカープールを実装してください。",
      },
    ],
  });

  console.log(response);
}

main().catch(console.error);
```

---

## ベンチマーク結果とコスト比較

Anthropicの公式評価結果です：

### SWE-bench Multilingual / BrowseComp

| 設定 | スコア | Sonnet単独比コスト |
| --- | --- | --- |
| Sonnet単独 | ベースライン | 100% |
| **Sonnet + Opus Advisor** | **+2.7pp向上** | **-11.9%（削減）** |
| Haiku単独 | 低スコア | 最安 |
| **Haiku + Opus Advisor** | **BrowseComp: 41.2%** | **Sonnetより85%安** |
| Opus単独 | 最高品質 | 最高コスト |

[公式ブログ「The advisor strategy」](https://claude.com/blog/the-advisor-strategy) より。

**ポイント：**

* **Sonnet + Opus Advisor** は、スコアを向上させながらコストも下げられる理想的なトレードオフ。Advisorが短い計画テキストのみを生成し、Executorが全出力を低コストレートで生成するため
* **Haiku + Opus Advisor** は、Sonnet単独より85%安いながらBrowseCompスコアが2倍以上に。高ボリューム・コスト感度の高いタスクに最適

---

## レスポンス構造の理解

Advisor呼び出しが発生した場合、アシスタントのコンテンツには `server_tool_use` と `advisor_tool_result` ブロックが含まれます：

```
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Advisorに相談してみます。"
    },
    {
      "type": "server_tool_use",
      "id": "srvtoolu_abc123",
      "name": "advisor",
      "input": {}
    },
    {
      "type": "advisor_tool_result",
      "tool_use_id": "srvtoolu_abc123",
      "content": {
        "type": "advisor_result",
        "text": "チャネルベースの協調パターンを使用してください。シャットダウン時のドレインが肝心で..."
      }
    },
    {
      "type": "text",
      "text": "以下の実装をご提案します..."
    }
  ]
}
```

`server_tool_use.input` は常に空（`{}`）です。サーバーが自動的に会話履歴全体をAdvisorに渡します。

### 使用量の確認

Advisorトークンはトップレベルの `usage` には含まれず、`usage.iterations[]` で確認できます：

```
{
  "usage": {
    "input_tokens": 412,
    "output_tokens": 531,
    "iterations": [
      {
        "type": "message",
        "input_tokens": 412,
        "output_tokens": 89
      },
      {
        "type": "advisor_message",
        "model": "claude-opus-4-6",
        "input_tokens": 823,
        "output_tokens": 1612
      },
      {
        "type": "message",
        "input_tokens": 1348,
        "output_tokens": 442
      }
    ]
  }
}
```

`type: "advisor_message"` のイテレーションはOpusのレートで課金されます。

---

## マルチターン会話での実装

マルチターン会話では、`advisor_tool_result` ブロックを含むアシスタントのコンテンツをそのまま次のリクエストに渡す必要があります：

```
import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": "claude-opus-4-6",
    }
]

messages = [
    {
        "role": "user",
        "content": "Goでグレースフルシャットダウン付きの並行ワーカープールを実装してください。",
    }
]

# 1ターン目
response = client.beta.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    betas=["advisor-tool-2026-03-01"],
    tools=tools,
    messages=messages,
)

# advisor_tool_result を含むすべてのコンテンツをそのまま追加
messages.append({"role": "assistant", "content": response.content})

# 2ターン目
messages.append({
    "role": "user",
    "content": "最大インフライト数を10に制限してください。",
})

response = client.beta.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    betas=["advisor-tool-2026-03-01"],
    tools=tools,
    messages=messages,
)
```

> フォローアップのターンで `tools` から advisor ツールを除外すると、`400 invalid_request_error` が発生します。会話中は必ず同じ `tools` 配列を維持してください。

---

## Advisor Prompt Caching

長期エージェントループでは、Advisor側のプロンプトキャッシュを有効にするとコストをさらに削減できます：

```
tools = [
    {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": "claude-opus-4-6",
        "caching": {"type": "ephemeral", "ttl": "5m"},  # または "1h"
    }
]
```

**有効にするタイミング：**

| Advisor呼び出し回数 | 推奨 |
| --- | --- |
| 2回以下 | キャッシュ無効（書き込みコストが上回る） |
| **3回以上** | **キャッシュ有効（効果あり）** |

> `clear_thinking` 設定で `keep` に `"all"` 以外を使用すると、Advisorのキャッシュがミスします。長期ループでOpusを使用する場合は `keep: "all"` を設定してください。

---

## コーディングタスク向けシステムプロンプト

Anthropicが推奨するシステムプロンプトパターンです。内部評価でAdvisorの呼び出しタイミングを最適化し、「Sonnet相当のコストでOpus相当の品質」を達成したパターンです：

### タイミング指示ブロック（Executorシステムプロンプトの先頭に追加）

```
You have access to an `advisor` tool backed by a stronger reviewer model. It takes NO parameters — when you call advisor(), your entire conversation history is automatically forwarded.

Call advisor BEFORE substantive work — before writing, before committing to an interpretation, before building on an assumption. If the task requires orientation first (finding files, fetching a source, seeing what's there), do that, then call advisor.

Also call advisor:
- When you believe the task is complete. BEFORE this call, make your deliverable durable: write the file, save the result, commit the change.
- When stuck — errors recurring, approach not converging.
- When considering a change of approach.
```

### 簡潔化指示（コスト削減）

Advisor出力トークンを約35〜45%削減できる一行指示：

```
The advisor should respond in under 100 words and use enumerated steps, not explanations.
```

---

## 他のツールとの組み合わせ

Advisor Toolはweb\_searchやカスタムツールと同時に使用できます：

```
tools = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5,
    },
    {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": "claude-opus-4-6",
    },
    {
        "name": "run_bash",
        "description": "Bashコマンドを実行",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
        },
    },
]
```

ExecutorはWebを検索し、Advisorに相談し、Bashコマンドを実行する、という複合的なタスクを1ターンで実行できます。

**コスト制御のヒント：**

```
# 会話レベルでAdvisor呼び出しを制限する場合
advisor_call_count = 0
MAX_ADVISOR_CALLS = 5

for response in responses:
    for block in response.content:
        if block.type == "server_tool_use" and block.name == "advisor":
            advisor_call_count += 1

# 上限に達したらtoolsからadvisorを除去し、
# messages historyからadvisor_tool_resultブロックも削除すること
```

---

## 制限事項・注意点

| 制限 | 詳細 |
| --- | --- |
| Advisorはストリームしない | Advisor実行中は出力が停止。SSE keepaliveが約30秒ごとに送信 |
| 会話レベルのmax\_usesなし | クライアント側でカウントが必要 |
| `max_tokens`はExecutorのみ | Advisorのトークンに上限は適用されない |
| Priority Tier | ExecutorのPriority TierはAdvisorには適用されない |
| Claude API（Anthropic）のみ | 現在はClaude直接APIのみ対応 |

---

## まとめ

Advisor Toolは「Opusの知能をSonnetのコストで部分的に活用する」というアプローチを実現します：

* **導入コスト最小**: 既存のAPIコードに `betas=["advisor-tool-2026-03-01"]` と `tools` 配列を追加するだけ
* **コスト削減**: Sonnet + Opus AdvisorでSonnet単独より11.9%安く、2.7pp品質向上
* **スケーラブル**: `max_uses` でリクエストごとのAdvisor呼び出し数を制限可能
* **将来性**: 長期エージェントループには `caching` 設定でさらにコスト最適化

まずは `max_uses: 2` など小さな設定でお試しいただき、ご自身のワークロードで効果を測定されることをおすすめします。

---

## 参考リンク
