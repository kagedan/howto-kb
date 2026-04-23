---
id: "2026-04-11-claude-46-web-search-dynamic-filtering入門-精度11向上トーク-01"
title: "Claude 4.6 Web Search Dynamic Filtering入門 — 精度11%向上・トークン24%削減の実装"
url: "https://qiita.com/kai_kou/items/f224054baeab92dc2ad6"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

Claude 4.6（Opus 4.6 / Sonnet 4.6）のリリースに合わせて、AnthropicはWeb Searchツールに**Dynamic Filtering**機能を追加しました。

これまでのWeb Searchは、検索結果のHTMLをそのままコンテキストウィンドウに読み込んでいました。Dynamic Filteringでは、Claudeがその場でフィルタリングコードを生成・実行し、関連するコンテンツだけを抽出してからコンテキストに読み込みます。

[Anthropicの公式ブログ](https://claude.com/blog/improved-web-search-with-dynamic-filtering)によると、この機能により2つのベンチマーク（BrowseComp・DeepsearchQA）の平均で**精度が11%向上し、入力トークンが24%削減**されています。

### この記事で学べること

* Dynamic Filteringの仕組みと従来の方式との違い
* `web_search_20260209`ツールバージョンの実装方法（Python / curl）
* コード実行が無料になる条件と設定
* ユースケース別の実装パターンとコスト計算

### 対象読者

* Claude APIでWeb Searchを使っているエンジニア
* RAGエージェントや検索エージェントのコスト・精度を改善したい方

### 前提環境

* Python 3.10以上
* anthropic SDK（最新版）
* `ANTHROPIC_API_KEY` 設定済み
* Claude Console でWeb Search有効化済み（組織管理者設定）

## TL;DR

* `web_search_20260209`に変更するだけでDynamic Filtering有効
* Claude Opus 4.6 / Sonnet 4.6のみ対応（Claude 3系・4.5系は旧バージョン使用）
* コード実行はWeb Search / Web Fetchと同時使用時は**無料**
* Google Vertex AIでは現在未対応（Claude API・Microsoft Azureのみ）

## Dynamic Filteringとは

### 従来のWeb Searchの問題点

旧バージョン（`web_search_20250305`）のWeb Searchでは、検索結果を次の順序で処理していました。

```
クエリ実行 → 複数URLのHTML全体を取得 → 全HTMLをコンテキストに読み込み → Claudeが回答生成
```

HTMLには本文以外にもナビゲーション、広告、関連記事リンクなどが含まれます。技術ドキュメントや論文の調査では、実際に必要な情報が全体の10〜30%程度であることも珍しくなく、**不要なコンテンツがトークンを無駄に消費**していました。

### Dynamic Filteringの仕組み

新バージョン（`web_search_20260209`）では、コード実行ステップが追加されます。

```
クエリ実行 → HTML取得 → [Claudeがフィルタリングコードを生成・実行] → 関連コンテンツのみ抽出 → コンテキスト読み込み → 回答生成
```

Claudeはサンドボックス環境でPythonなどのコードを実行し、クエリに関連するテキストのみを抽出します。このフィルタリング処理に使うコード実行は、Web SearchまたはWeb Fetchと組み合わせた場合は**追加料金なし**です。

### パフォーマンス改善の数値

[Anthropicの公式ブログ](https://claude.com/blog/improved-web-search-with-dynamic-filtering)が公開しているベンチマーク結果：

| モデル | Dynamic Filteringなし | Dynamic Filteringあり | 改善率 |
| --- | --- | --- | --- |
| Claude Sonnet 4.6 | 52.6% F1 | 59.4% F1 | +6.8pp（+12.9%） |
| Claude Opus 4.6 | 69.8% F1 | 77.3% F1 | +7.5pp（+10.7%） |
| 平均 | — | — | **+11%精度向上** |

入力トークンは平均**24%削減**。特に以下のユースケースで効果が顕著です：

* 技術ドキュメントの調査
* 文献レビューと引用検証
* 複数ソースを横断するリサーチ
* 回答のファクトチェック

## 実装方法

### 基本的な使い方（Python）

`type`フィールドのツールバージョンを変更するだけです。

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",   # claude-opus-4-6 も可
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Claude 4.6のEffortパラメータの推奨設定と、Adaptive Thinkingとの違いを調べてください。"
        }
    ],
    tools=[{
        "type": "web_search_20260209",   # ← ここを変更
        "name": "web_search"
    }]
)

# レスポンスの最後のテキストブロックを表示
for block in response.content:
    if block.type == "text":
        print(block.text)
```

**旧バージョンとの変更点の比較：**

| 項目 | 旧バージョン | 新バージョン |
| --- | --- | --- |
| `type` | `web_search_20250305` | `web_search_20260209` |
| Dynamic Filtering | なし | あり |
| コード実行（無料） | 対象外 | ✅ |
| 対応モデル | Claude 3.x〜4.6 | Claude Opus/Sonnet 4.6のみ |

### curl での例

```
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-sonnet-4-6",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "最新のLLMベンチマーク（MMLU・HumanEval等）の結果と主要モデルの比較を調査してください。"
            }
        ],
        "tools": [{
            "type": "web_search_20260209",
            "name": "web_search"
        }]
    }'
```

### Web Fetchとの組み合わせ

Web FetchツールにもDynamic Filteringに対応した新バージョン（`web_fetch_20260209`）があります。両方を組み合わせる場合は次のように指定します：

```
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=8192,
    messages=[{
        "role": "user",
        "content": (
            "https://platform.claude.com/docs/en/about-claude/models/overview から"
            "最新モデル一覧・コンテキスト長・料金を取得して表にまとめてください。"
        )
    }],
    tools=[
        {
            "type": "web_search_20260209",
            "name": "web_search"
        },
        {
            "type": "web_fetch_20260209",    # ← こちらも新バージョン
            "name": "web_fetch"
        }
    ]
)
```

どちらか一方がリクエストに含まれていれば、コード実行は無料になります。

### ドメインフィルタリングとの組み合わせ

`allowed_domains` / `blocked_domains` は新バージョンでも同様に使用できます：

```
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": "Anthropic Claude APIの最新トークン料金を調べてください。"
    }],
    tools=[{
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 3,
        "allowed_domains": ["anthropic.com", "platform.claude.com"]   # 信頼ドメインのみ
    }]
)
```

### ストリーミングでの実装

長い回答が予想される場合はストリーミングが推奨されます：

```
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=8192,
    messages=[{
        "role": "user",
        "content": "最新の主要LLMフレームワーク（LangChain・LangGraph・CrewAI等）のGitHubスター数と最新バージョンを横断調査してください。"
    }],
    tools=[{"type": "web_search_20260209", "name": "web_search"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## コスト計算

### 料金体系

[公式価格ページ](https://platform.claude.com/docs/en/about-claude/pricing)によると、Web Search利用時の料金は次のとおりです：

| 項目 | 料金 |
| --- | --- |
| Web Searchリクエスト | $10 / 1,000回 |
| コード実行（Web Search/Fetch併用時） | **無料** |
| Claude Sonnet 4.6 入力トークン | $3 / MTok |
| Claude Sonnet 4.6 出力トークン | $15 / MTok |
| Claude Opus 4.6 入力トークン | $5 / MTok |
| Claude Opus 4.6 出力トークン | $25 / MTok |

### Dynamic Filteringによるコスト削減の試算

1回のWeb Searchで10,000入力トークンを消費するケースでは：

| 条件 | トークン消費 | コスト（Sonnet 4.6） |
| --- | --- | --- |
| 旧バージョン（フィルタなし） | 10,000 | $0.030 |
| Dynamic Filtering適用後（-24%） | 7,600 | $0.023 |
| **節約額** | 2,400トークン | **$0.007/回** |

月1,000回検索する場合、トークンコストだけで約$7の削減になります。

### 利用状況の確認

レスポンスの`usage`フィールドで検索回数とトークン使用量を確認できます：

```
response = client.messages.create(...)

print(f"入力トークン: {response.usage.input_tokens}")
print(f"出力トークン: {response.usage.output_tokens}")
print(f"Web Search実行回数: {response.usage.server_tool_use.web_search_requests}")
```

## 注意点

### 対応環境

Dynamic Filteringは現在、すべての環境では利用できません：

| 環境 | Dynamic Filtering | 基本Web Search |
| --- | --- | --- |
| Claude API（直接） | ✅ | ✅ |
| Microsoft Azure | ✅ | ✅ |
| Google Vertex AI | ❌ | ✅ |
| Amazon Bedrock | ❌ | ✅（Mythos Previewを除く） |

Vertex AIやBedrockを使用している場合は、引き続き`web_search_20250305`を使用します。

### 対応モデル

Dynamic Filteringは**Claude Opus 4.6 / Sonnet 4.6のみ**対応しています。Claude 3系や4.5系に対して`web_search_20260209`を指定してもエラーになるため、モデルに応じてツールバージョンを切り替える必要があります：

```
def get_web_search_tool(model: str) -> dict:
    """モデルに応じて適切なWeb Searchツールバージョンを返す"""
    dynamic_filtering_models = {"claude-opus-4-6", "claude-sonnet-4-6"}
    if model in dynamic_filtering_models:
        return {"type": "web_search_20260209", "name": "web_search"}
    else:
        return {"type": "web_search_20250305", "name": "web_search"}
```

### コンソール設定

Web Searchを使用するには、組織の管理者が[Claude Console](https://platform.claude.com/settings/privacy)（要ログイン）でWeb Searchを有効化する必要があります。個人のAPIキーだけでは有効になりません。

## まとめ

Claude 4.6のDynamic FilteringはWeb Searchの精度とコスト効率の両方を改善します。

* **移行コスト最小**: `web_search_20250305` → `web_search_20260209` のバージョン名変更のみ
* **コード実行は無料**: Web SearchかWeb Fetchと組み合わせれば追加料金なし
* **精度+11%・トークン-24%**: 技術ドキュメント調査・文献レビュー等で特に効果大

Claude APIを使ったRAGエージェントや検索エージェントを構築している場合、`web_search_20260209`へ移行するだけで、コードの変更を最小限に抑えながら検索精度とコスト効率の両方を改善できます。

## 参考リンク
