---
id: "2026-03-29-symphonyのトラッカーをlinearからnotionに変えたら一人開発がめちゃくちゃ捗った話-01"
title: "SymphonyのトラッカーをLinearからNotionに変えたら、一人開発がめちゃくちゃ捗った話"
url: "https://zenn.dev/naoya5/articles/symphony-notion-orchestrator"
source: "zenn"
category: "ai-workflow"
tags: ["OpenAI", "zenn"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## TL;DR

OpenAI が公開したエージェントオーケストレーター **Symphony** は、デフォルトで Linear をタスクトラッカーとして使います。これを **Notion に差し替えた**ところ、普段のワークフローと統一できて一人開発の生産性が大きく向上しました。本記事では、なぜ Notion にしたのか・どう変えたのか・使ってみてどうだったかをまとめます。

## Symphony とは何か

<https://github.com/openai/symphony>

[Symphony](https://github.com/openai/symphony) は、OpenAI が公開した**エージェントオーケストレーションサービス**です。

やることはシンプルで、次の 3 ステップを自動で回します：

1. **タスクトラッカーをポーリング**して「Ready for Dev」のタスクを見つける
2. タスクごとに**隔離されたワークスペース**を作り、コーディングエージェント（Codex）を起動する
3. エージェントがコードを書き、**ステータスを自動更新**する

つまり、「Issue を立てたら勝手にコードが書かれる」仕組みです。

これは最近注目されている**ハーネスエンジニアリング**の考え方そのものです。エージェントが最大限の力を発揮できるよう「ハーネス（制御構造）」を整える ── Symphony はその実装例と言えます。ポーリング間隔、ワークスペースの分離、プロンプトテンプレート、リトライ戦略といった「エージェントの動き方」を設定ファイルで宣言的に制御する設計になっています。

## なぜ Linear → Notion にしたのか

理由はシンプルで、**普段から Notion を使っているから**です。

一人で開発していると、ドキュメント・タスク管理・ナレッジベースを一箇所にまとめたくなります。Linear は開発チーム向けの素晴らしいツールですが、一人開発で Notion と Linear を行き来するのはオーバーヘッドでした。

Notion にトラッカーを統一することで：

* **タスク作成から完了まで Notion だけで完結**します
* ドキュメントやメモと同じワークスペースにタスクがあります
* Notion のデータベースビュー（カンバン、テーブル等）でそのまま管理できます

## アーキテクチャ

Notion 版 Symphony の全体フローはこうなります：

ポイントは、**Notion が唯一の入出力インターフェース**になっていることです。開発者は Notion にタスクを書くだけ。あとは Symphony がポーリングし、Codex がコードを書き、結果が Notion に返ってきます。

## どう変えたか

### 1. Notion API アダプターの実装

Symphony のトラッカー層はアダプターパターンで設計されています。Linear アダプターを削除し、Notion REST API を叩く `NotionAdapter` を実装しました。

lib/symphony\_elixir/intake/sources/notion\_adapter.ex

```
defmodule SymphonyElixir.Intake.Sources.NotionAdapter do
  @base_url "https://api.notion.com/v1"

  def fetch_candidates(api_key, database_id, ready_state) do
    filter = %{
      "filter" => %{
        "property" => "Status",
        "status" => %{"equals" => ready_state}
      }
    }

    post("#{@base_url}/databases/#{database_id}/query", filter, api_key)
  end

  def update_status(api_key, page_id, status) do
    body = %{
      "properties" => %{
        "Status" => %{"status" => %{"name" => status}}
      }
    }

    patch("#{@base_url}/pages/#{page_id}", body, api_key)
  end
end
```

### 2. WORKFLOW.md の設定

Symphony の設定は `WORKFLOW.md` のフロントマターで宣言的に書きます。Linear 固有のフィールドを Notion 用に差し替えるだけで済みました。

WORKFLOW.md

```
tracker:
  kind: notion
  api_key: $NOTION_API_KEY
  database_id: $NOTION_DATABASE_ID
  status_property: Status
  title_property: Name
  ready_state: Ready for Dev
  active_states:
    - Ready for Dev
    - In Progress
  terminal_states:
    - Done
```

### 3. Notion データベースの準備

必要なのは 2 つのプロパティだけ：

| プロパティ | 型 | 用途 |
| --- | --- | --- |
| **Name** | タイトル | タスク名 |
| **Status** | ステータス | `Ready for Dev` → `In Progress` → `Done` |

Notion のインテグレーションを作成し、データベースに接続すれば準備完了です。

## 使ってみた感想

### 良かった点

* **ゼロコンテキストスイッチ**: タスクを書く場所と管理する場所が同じ Notion なので、思考が途切れません
* **データベースビューの柔軟さ**: カンバン表示で進捗を見つつ、テーブル表示で一覧を確認できます
* **API がシンプル**: Notion の REST API は直感的で、Linear の GraphQL より取り回しが楽でした
* **ブロック → Markdown 変換**: タスクの説明を Notion のリッチテキストで書いても、エージェントには Markdown として渡せます

### 注意点

* Notion API のレートリミット（3 requests/sec）があるので、ポーリング間隔は余裕を持たせた方がいいです
* ステータスプロパティの値は完全一致で判定されるため、表記ゆれに注意してください

## まとめ

Symphony のトラッカーを Linear から Notion に変えた結果、**一人開発のワークフローが一つのツールに収束**しました。

ハーネスエンジニアリングの文脈で言えば、エージェントの「ハーネス」を自分のワークフローに最適化した形です。Symphony のアダプターパターンのおかげで、変更は最小限で済みました。

普段から Notion を使っていて、エージェント駆動の開発に興味がある人は、ぜひ試してみてください。
