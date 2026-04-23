---
id: "2026-03-27-claude-memory入門-3層アーキテクチャと過去チャット検索の全貌-01"
title: "Claude Memory入門 — 3層アーキテクチャと過去チャット検索の全貌"
url: "https://qiita.com/kai_kou/items/c5c3d7a04fec298a9e2c"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Gemini", "GPT", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## はじめに

2026年3月、AnthropicはClaude Memoryを**全プラン（Free含む）へ展開**しました。これまでは有料プラン限定だったメモリ機能が、無料ユーザーも含めた全ユーザーに開放されています。

Claudeのメモリシステムは単なる「会話履歴の保存」ではなく、目的の異なる**3層のアーキテクチャ**で構成されています。本記事では、各レイヤーの仕組みと実装方法を公式ドキュメントをもとに解説します。

### この記事で学べること

* Claudeのメモリ3層アーキテクチャの全貌
* Chat Memory（メモリ合成）の動作原理
* 過去チャット検索（RAGベースのツールコール）の使い方
* API Memory Toolの実装方法
* エンタープライズ環境での管理・制御方法
* ChatGPT / Gemini / Grok からのメモリインポート

### 対象読者

* AnthropicのAPIやClaudeを開発に使っているエンジニア
* AIエージェントに長期記憶を持たせたい開発者
* エンタープライズでClaude利用ポリシーを管理している担当者

---

## TL;DR

* Claudeメモリは **Chat Memory / Project Memory / API Memory Tool** の3層構成
* Chat Memoryは2026年3月から\*\*全プラン（Free含む）\*\*で利用可能
* 過去チャット検索（`conversation_search` / `recent_chats`）は**有料プラン限定**のRAG機能
* API Memory Toolは`type: "memory_20250818"`で有効化し、6操作でファイル型メモリを管理
* エンタープライズはOrganization Settingsで組織全体のメモリを制御可能

---

## Claudeメモリの3層アーキテクチャ

Claudeのメモリは、利用シーンに応じた3つの独立したレイヤーで構成されています。

| レイヤー | 対象 | 利用可能プラン | 特徴 |
| --- | --- | --- | --- |
| Layer 1: Chat Memory | 一般ユーザー | Free, Pro, Max, Team, Enterprise | 会話を自動合成・24時間ごと更新 |
| Layer 2: Project Memory | プロジェクト単位 | Pro以上 | プロジェクトごとに独立したメモリ空間 |
| Layer 3: API Memory Tool | 開発者・APIユーザー | API/Enterprise | ファイル型永続メモリをPythonで操作 |

これらは「高度なバージョンに置き換わる」関係ではなく、それぞれ異なる役割を持つ並列的なツールです。

---

## Layer 1: Chat Memory（メモリ合成）

### 動作原理

Chat Memoryの中核は\*\*Memory Synthesis（メモリ合成）\*\*です。

Claudeは会話内容を**約24時間ごとに自動処理**し、長期的に価値のある情報を抽出・要約します。

合成される情報の例:

* 職業・役職
* 使用言語の好み
* よく使うツールや技術スタック
* 繰り返し登場する個人的なコンテキスト

合成されたメモリはユーザーのMemoryプロファイルに保存され、**以降のすべての会話に自動的にロード**されます。

### 設定方法

メモリの有効/無効は `Settings > Capabilities` から切り替えられます。

* **Pause Memory**: 既存のメモリは保持しつつ、新しいメモリの生成・使用を停止
* **Incognito Chat**: メモリに保存されない一時会話モード

> 削除した会話はメモリ合成から除外されます。会話削除後24時間以内にメモリが更新されます。

---

## Layer 2: Project Memory

プロジェクトには**独立したメモリ空間とプロジェクト要約**が割り当てられます。

* プロジェクト内のコンテキストは他のプロジェクトや通常の会話と**完全に分離**
* プロジェクト専用のコーディングスタイルやドメイン知識を蓄積可能
* チームでプロジェクトを共有している場合、メモリもチームに紐づく

---

## 過去チャット検索（Chat Search）

### 概要

Chat Searchは\*\*有料プラン（Pro, Max, Team, Enterprise）\*\*で利用可能なRAGベースの機能です。

Claudeに「以前〜について話した内容を探して」と伝えると、過去の会話を検索してコンテキストを取得します。この検索は**ツールコールとして透過的に実行**されるため、Claudeがいつどのようにメモリにアクセスしているかを確認できます。

### 使用するツール

過去チャット検索は2つの組み込みツールで実装されています。

**`conversation_search`** — キーワード・トピックで過去の会話を横断検索

```
# 内部的にはこのような操作が行われる（概念コード）
conversation_search(
    query="Pythonの非同期処理",
    date_range={"start": "2026-01-01", "end": "2026-03-26"}
)
```

**`recent_chats`** — 最近の会話をタイムスタンプ付きで取得

```
# ソート順やページネーション、プロジェクトフィルタに対応
recent_chats(
    sort="reverse_chronological",
    before="2026-03-26T00:00:00Z",
    project_filter="zenn-blog-project"
)
```

検索結果は**会話全体ではなく関連部分のみ**を返すため、トークン効率が高い設計です。

> インコグニートチャットは過去チャット検索の対象外です。プライバシーに配慮した設計になっています。

---

## Layer 3: API Memory Tool

### 概要

API Memory Toolは、APIを使って開発者がアプリケーションに**セッションをまたいだ永続メモリ**を実装できる機能です。

[公式ドキュメント](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)によると、以下のモデルで利用可能です:

* Opus 4.6, 4.5, 4.1, 4
* Sonnet 4.6, 4.5, 4
* Haiku 4.5

### 基本実装

```
import anthropic

client = anthropic.Anthropic()

# メモリツールを有効化して会話を開始
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=[
        {
            "type": "memory_20250818",  # メモリツールの識別子
            "name": "memory"
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "私はPythonエンジニアで、FastAPIを主に使っています。覚えておいてください。"
        }
    ]
)

print(response.content)
```

### 6つのメモリ操作

API Memory Toolは `/memories` ディレクトリへのファイル操作として実装されており、6つの操作をサポートします。

| 操作 | 用途 | 説明 |
| --- | --- | --- |
| `view` | 読み取り | メモリファイルの内容確認 |
| `create` | 作成 | 新規メモリファイルの作成 |
| `str_replace` | 更新 | 文字列置換による部分更新 |
| `insert` | 挿入 | 指定行への内容挿入 |
| `delete` | 削除 | メモリファイルの削除 |
| `rename` | 名前変更 | ファイル名の変更 |

### メモリの構造化テンプレート

公式ドキュメントによると、メモリ記録には構造化されたテンプレートが推奨されています。

```
# ユーザープロファイル

## ルール/事実
ユーザーはPythonエンジニアでFastAPIを主に使用している。

## 理由
APIサーバー開発の質問に対して、FastAPIベースのサンプルコードを提供するため。

## 適用シーン
API実装、バックエンド開発、パフォーマンス最適化の質問時に参照する。
```

> API Memory Toolのオーバーヘッドは約2,500トークンです。追加料金はなく、標準レートで課金されます。

### Context Editingとの組み合わせ

長期稼働するエージェントシステムでは、**Context Editing**（コンテキスト自動圧縮）との組み合わせが推奨されています。

```
# コンテキストが閾値を超えたとき古いツール結果を自動削除
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=[
        {"type": "memory_20250818", "name": "memory"}
    ],
    # context_editingを有効にすることで
    # 長期エージェントループでもコンテキスト超過を防げる
    system="You are a persistent assistant. Use memory tool to store important user information.",
    messages=conversation_history
)
```

---

## クロスプラットフォームメモリインポート

[Fast Companyの報道](https://www.fastcompany.com/91501002/anthropic-claude-app-import-chats-from-open-ai-chatgpt-gemini-copilot-memory-tool)によると、AnthropicはChatGPT, Gemini, Grokからメモリをインポートできる機能を提供しています（有料プラン向け、実験的）。

**対応インポート元:**

* ChatGPT（OpenAI）
* Gemini（Google）
* Grok（xAI）
* Microsoft Copilot

**インポート手順（概要）:**

1. 移行元AIツールのメモリデータをエクスポート
2. AnthropicのインポートツールでClaude向けプロンプトに変換
3. Claudeのメモリに貼り付け

他のAIツールから乗り換える際のコンテキスト継続性が大幅に向上します。

---

## エンタープライズ環境での管理

### 組織レベルの制御

**Organization Settings > Capabilities** から組織全体のメモリ機能を管理できます。

| 設定 | 効果 |
| --- | --- |
| 組織全体でメモリ無効化 | 全ユーザーのメモリデータを即時削除 |
| ユーザー個別の有効化を許可 | オーナーが許可した場合のみ個人設定変更可 |
| データ保持ポリシー連動 | 会話削除時にサマリーも自動削除 |

> オーナーが組織全体のメモリを無効化すると、**全ユーザーのメモリデータが即時・永久削除**されます。この操作は元に戻せません。

### セキュリティ特性

* メモリデータは**保存時・転送時ともに暗号化**
* Enterprise/APIプランでは**デフォルトでトレーニングデータに使用されない**
* SSO（シングルサインオン）と管理ツールによる組織レベルのアクセス制御

---

## まとめ

Claudeのメモリシステムは、目的と利用シーンに応じた3層構成で設計されています。

* **Chat Memory（Layer 1）**: 2026年3月から全ユーザーに開放。24時間ごとの自動合成でコンテキスト継続性を提供
* **Project Memory（Layer 2）**: プロジェクト単位の独立メモリ空間で、チーム開発にも対応
* **API Memory Tool（Layer 3）**: `type: "memory_20250818"` で有効化し、6操作でファイル型永続メモリを管理

エンジニアがAPIで長期稼働エージェントを構築する際は、API Memory ToolとContext Editingの組み合わせが推奨構成です。エンタープライズ利用では、Organization Settingsによる組織全体の制御が可能です。

---

## 参考リンク
