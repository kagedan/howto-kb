---
id: "2026-03-30-claude-api-web-search-dynamic-filtering入門-精度11向上トー-01"
title: "Claude API Web Search Dynamic Filtering入門 — 精度11%向上・トークン24%削減の実装ガイド"
url: "https://qiita.com/kai_kou/items/89ab96568b2ec6a37be1"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

Claude API の Web Search ツールが大幅に強化されました。新バージョン `web_search_20260209` では**ダイナミックフィルタリング**が利用可能になり、検索精度が平均11%向上し、入力トークンを24%削減できます。

本記事では以下を解説します。

* ダイナミックフィルタリングの仕組みと従来との違い
* Python での実装方法
* ベンチマーク結果の読み方
* コスト管理と注意点

**対象読者**: Claude API を使った RAG・エージェント・情報収集システムを構築しているエンジニア

**前提環境**:

* Python 3.9+
* `anthropic` SDK（最新版）
* Anthropic API キー（Web Search 有効化済み）

> Web Search ツールを使用するには、[Claude Console](https://platform.claude.com/settings/privacy) の管理者設定で有効化が必要です。

## TL;DR

* `web_search_20260209` に変更するだけで Dynamic Filtering が有効になる
* Claude がコードを書いてHTML全体を読まず必要部分だけコンテキストに取り込む
* BrowseComp で Sonnet 4.6: 33.3% → 46.6%、Opus 4.6: 45.3% → 61.6%
* Code Execution は Web Search/Fetch と同時使用時は**無料**
* Google Vertex AI では Dynamic Filtering は未対応（Claude API・Azure のみ）

---

## Dynamic Filtering とは

### 従来の Web Search の課題

従来の `web_search_20250305` では、Claude は次のように動作していました。

1. Web Search でページを取得
2. HTML 全体（ナビゲーション・広告・スクリプトタグを含む）をコンテキストに読み込む
3. 大量のノイズを含んだ状態で回答を生成

HTML ページには質問と無関係なコンテンツが大量に含まれており、これがトークンの無駄遣いと精度低下の原因になっていました。

### Dynamic Filtering の仕組み

新バージョン `web_search_20260209` では、Claude が**コードを書いて検索結果をフィルタリング**してからコンテキストに取り込みます。

```
[Web Search] → [HTML 取得] → [Claude がフィルタコード実行] → [必要部分のみ抽出] → [コンテキストへ]
```

具体的には:

* Claude が Python コードを自動生成し、HTML をパース
* 質問に関係する部分のみ抽出してコンテキストに追加
* ナビゲーション・広告・スクリプトなど不要部分を除外

このため `web_search_20260209` では **code execution ツールが必須**です。ただし Web Search/Fetch と組み合わせた場合、code execution の使用料は**無料**になります。

---

## ベンチマーク結果

Anthropic が2つのベンチマークで検証した結果を公式ドキュメントより引用します。

### BrowseComp（複数サイトを横断して特定情報を探すベンチマーク）

| モデル | フィルタなし | フィルタあり | 改善幅 |
| --- | --- | --- | --- |
| Sonnet 4.6 | 33.3% | 46.6% | +13.3pp |
| Opus 4.6 | 45.3% | 61.6% | +16.3pp |

### DeepsearchQA（多段階リサーチの F1 スコア）

| モデル | フィルタなし | フィルタあり | 改善幅 |
| --- | --- | --- | --- |
| Sonnet 4.6 | 52.6% | 59.4% | +6.8pp |
| Opus 4.6 | 69.8% | 77.3% | +7.5pp |

**平均: 精度+11%、入力トークン-24%**

Dynamic Filtering は特に以下のユースケースで効果的です。

* 技術ドキュメントの検索
* 文献レビューと引用検証
* 技術リサーチ
* 回答のグラウンディングと検証

---

## 実装ガイド

### インストール

```
pip install anthropic --upgrade
```

### 基本的な使い方（Dynamic Filtering 有効）

`web_search_20260209` を指定するだけで Dynamic Filtering が自動的に有効になります。

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "AAPLとGOOGLの現在の株価を調べ、どちらのP/Eレシオが良いか計算してください。",
        }
    ],
    # web_search_20260209 を指定すると Dynamic Filtering が自動的に有効になる
    # 公式ドキュメントによると code execution ツールが内部で有効化される
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
)
print(response)
```

Dynamic Filtering を使わない場合（旧バージョン）は以下のとおりです。

```
# 旧バージョン（Dynamic Filtering なし）
tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]
```

### オプションパラメータの活用

```
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "最新のLLMベンチマーク結果を教えてください。"}
    ],
    tools=[
        {
            "type": "web_search_20260209",
            "name": "web_search",
            # 最大検索回数（コスト制御に有効）
            "max_uses": 3,
            # 特定ドメインのみ検索（省略可）
            "allowed_domains": ["arxiv.org", "paperswithcode.com"],
            # ロケーション指定（省略可）
            "user_location": {
                "type": "approximate",
                "city": "Tokyo",
                "region": "Tokyo",
                "country": "JP",
                "timezone": "Asia/Tokyo"
            }
        }
    ],
)
```

### レスポンスの構造

Dynamic Filtering 有効時のレスポンスには、検索結果の引用が自動的に付与されます。

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[
        {"role": "user", "content": "Python 3.13 の新機能を教えてください。"}
    ],
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
)

# テキスト内容と引用を取り出す
for block in response.content:
    if block.type == "text":
        print(block.text)
        # 引用情報が含まれる場合
        if hasattr(block, "citations") and block.citations:
            for citation in block.citations:
                print(f"  出典: {citation.title} - {citation.url}")

# Web Search の使用回数を確認
print(f"Web Search 使用回数: {response.usage.server_tool_use.web_search_requests}")
```

### ストリーミング対応

```
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "今日のAI業界の最新ニュースをまとめてください。"}
    ],
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

## コスト管理

### 料金体系

| 項目 | 料金 |
| --- | --- |
| Web Search | $10 / 1,000回 |
| Code Execution（Web Search/Fetch 同時使用） | **無料** |
| Code Execution（単独使用） | 実行時間課金 |
| 検索結果トークン | 通常の入力トークンとして課金 |

### `max_uses` によるコスト上限設定

```
# 1リクエストあたり最大3回までに制限
tools=[{
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 3
}]
```

`max_uses` を超えた場合、レスポンス内に `max_uses_exceeded` エラーコードが返り、その検索は課金されません。

### Sonnet 4.6 vs Opus 4.6 のコスト比較

Dynamic Filtering 使用時、Sonnet 4.6 は両ベンチマークでトークンコストが減少しますが、Opus 4.6 は BrowseComp でトークンコストが増加する場合があります。本番環境では実際のクエリセットで事前評価することが推奨されます。

---

## 注意点

### プラットフォーム対応状況

| プラットフォーム | Dynamic Filtering | 基本 Web Search |
| --- | --- | --- |
| Claude API | ✅ | ✅ |
| Microsoft Azure | ✅ | ✅ |
| Google Vertex AI | ❌ | ✅ |

Google Vertex AI では `web_search_20250305`（Dynamic Filtering なし）のみ利用可能です。

### Zero Data Retention（ZDR）

Dynamic Filtering が有効な場合、ZDR（ゼロデータリテンション）の対象外になります。セキュリティポリシー上 ZDR が必須の場合は、`web_search_20250305` を使用してください。

### エラーハンドリング

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[
        {"role": "user", "content": "最新のニュースを検索してください。"}
    ],
    tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 2}],
)

# エラーブロックのチェック
for block in response.content:
    if block.type == "web_search_tool_result":
        content = block.content
        if isinstance(content, dict) and content.get("type") == "web_search_tool_result_error":
            error_code = content.get("error_code")
            if error_code == "max_uses_exceeded":
                print("Web Search の上限に達しました")
            elif error_code == "too_many_requests":
                print("レート制限に達しました。しばらく待ってから再試行してください。")
            elif error_code == "unavailable":
                print("Web Search が一時的に利用できません。")
```

主なエラーコード:

* `too_many_requests`: レート制限超過
* `invalid_input`: 無効な検索クエリ
* `max_uses_exceeded`: 最大使用回数超過
* `query_too_long`: クエリが最大長超過
* `unavailable`: 内部エラー

---

## 同時 GA になったツール

`web_search_20260209` と同時に、以下のツールも一般提供（GA）になりました。

| ツール | 用途 |
| --- | --- |
| Code Execution | コードの実行（Web Search/Fetch と同時使用時無料） |
| Memory Tool | 会話をまたいだ情報の永続化 |
| Programmatic Tool Calling | エージェント内でのツール呼び出し |
| Tool Search | 動的なツール探索 |
| Tool Use Examples | ツール使用例の提供 |

これらはすべてベータヘッダーなしで使用可能です。

---

## まとめ

Claude API Web Search の Dynamic Filtering で得られる主なメリットは以下のとおりです。

* **精度向上**: BrowseComp で最大+16.3pp、平均+11%
* **トークン削減**: 入力トークンを平均24%削減
* **移行コスト最小**: ツールバージョンを変更するだけで有効化可能
* **code execution 無料**: Web Search/Fetch と同時使用時は追加コストなし

特に技術ドキュメント検索・文献調査・情報グラウンディングを行うエージェントシステムにおいて効果的です。既存の `web_search_20250305` を使っている場合は `web_search_20260209` への移行を検討してください。

## 参考リンク
