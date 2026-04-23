---
id: "2026-04-21-claude-opus-47-開発者ツールガイド-task-budgetsultrareviewの実-01"
title: "Claude Opus 4.7 開発者ツールガイド — task budgets・/ultrareviewの実装"
url: "https://qiita.com/kai_kou/items/a84683cb778cf84ced64"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

## はじめに

2026年4月16日、Anthropicは[Claude Opus 4.7を正式リリース](https://www.anthropic.com/news/claude-opus-4-7)しました。モデル自体の性能向上（SWE-bench 87.6%、3.75MP Vision）は[別記事](https://zenn.dev/kai_kou/articles/238-claude-opus-47-release-api-guide)で解説済みです。

本記事では**エンジニアが即活用できる3つの開発者向け新機能**に絞って解説します。

### この記事で学べること

* **xhigh effortレベル**: 推論深度をきめ細かく制御するAPIパラメータ
* **Task budgets（ベータ）**: エージェントループのトークン上限を自動管理する仕組み
* **/ultrareviewコマンド**: Claude Codeで変更箇所のバグを検出する専用レビュー機能

### 対象読者

* Claude APIを使ったエージェントアプリケーションを開発している方
* Claude Codeを日常的に使っているエンジニア
* コスト管理と品質を両立したいAPIユーザー

---

## TL;DR

| 機能 | 区分 | 効果 |
| --- | --- | --- |
| xhigh effort | APIパラメータ | high〜maxの中間で推論深度を精密調整 |
| task budgets | APIベータ機能 | エージェントのトークン総消費量を上限設定 |
| /ultrareview | Claude Codeコマンド | 変更差分を読み込みバグ・設計問題を自動指摘 |

---

## 1. xhigh effortレベル

### 概要

Claude APIの`effort`パラメータに新しいレベル`xhigh`が追加されました。従来の`high`と`max`の間に位置する設定で、長時間の推論が必要な問題でレイテンシとコストのバランスをより精密に制御できます。

**effortレベルの一覧（低→高）**

| レベル | 用途 |
| --- | --- |
| `low` | 最も効率的。高速・低コスト優先のシンプルなタスク向け |
| `medium` | 標準的な推論（デフォルト）。速度とコストのバランス |
| `high` | 高い能力。複雑な推論・コーディング・分析向け |
| `xhigh` | **新規追加**。高難度エージェントタスク・コードレビュー向け |
| `max` | 最大推論。コスト上限なしの最高能力向け |

> Claude Codeでは全プラン（Pro・Max・Teams・Enterprise）で`xhigh`がデフォルトになりました。

### APIでの実装

```
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    output_config={
        "effort": "xhigh",
    },
    messages=[
        {
            "role": "user",
            "content": "このコードの設計上の問題点を網羅的に分析してください。",
        }
    ],
)

print(response.content[0].text)
```

`output_config.effort`に`"xhigh"`を指定するだけで有効になります。既存の`high`や`max`を使っている場合、`xhigh`への変更で推論品質とレイテンシのバランスが改善される可能性があります。

### いつxhighを使うか

* コードレビュー・リファクタリング提案
* 複数ファイルにまたがる依存関係の分析
* バグの根本原因調査
* `high`では不十分だが`max`はコスト的に過剰な場合

---

## 2. Task budgets（ベータ）

### 概要

Task budgetsは**エージェントループ全体で消費するトークン量に上限を設ける**ベータ機能です。思考トークン・ツール呼び出し・ツール結果・最終出力をすべて含む総トークン量を制御します。

モデルは内部でカウントダウンを持ち、残り予算を意識しながら作業の優先度を自動調整します。予算が逼迫してくると、重要度の低い作業を省略して主要タスクを完遂しようとします。

この機能が特に有効なのは、**人間が介在しない自律型エージェント**です。無制限に実行されるエージェントループのコストを予算で上限設定することで、予期せぬ高額請求を防止できます。

### 設定要件

* ベータヘッダー: `task-budgets-2026-03-13`
* 最低予算: **20,000トークン**（これ未満は設定不可）
* `output_config.task_budget`パラメータで指定

### APIでの実装

```
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=128000,
    output_config={
        "effort": "high",
        "task_budget": {
            "type": "tokens",
            "total": 50000,  # アドバイザリー目標値（ソフトヒント）
        },
    },
    messages=[
        {
            "role": "user",
            "content": "リポジトリ全体を調査してリファクタリング計画を提案してください。",
        }
    ],
    betas=["task-budgets-2026-03-13"],
)

print(response.content[0].text)

# 実際に消費されたトークン数を確認
usage = response.usage
print(f"入力: {usage.input_tokens} tokens")
print(f"出力: {usage.output_tokens} tokens")
```

### task\_budget の設定指針

| ユースケース | 推奨budget | 備考 |
| --- | --- | --- |
| 単一ファイルのコードレビュー | 20,000〜40,000 | 最低値付近で十分 |
| 中規模リポジトリ調査 | 50,000〜80,000 | ファイル数・複雑度で調整 |
| 大規模エージェントタスク | 100,000〜128,000 | `max_tokens`と合わせて調整 |

### 注意点

公式ドキュメントによると、**予算が過度に制限的な場合、モデルは処理を不完全に終えるか拒否することがあります**。まずは余裕ある予算で試し、ログで実際の消費量を確認してから最適値に絞り込む進め方が推奨されています。

```
# 使用量ログで実際の消費を把握
print(f"実際の消費: {response.usage.output_tokens} tokens / {50000} tokens 予算")
```

---

## 3. /ultrareviewコマンド

### 概要

Claude Codeに`/ultrareview`スラッシュコマンドが追加されました。変更した差分を自動読み込みし、**注意深いコードレビュアーなら発見するバグや設計上の問題**を指摘する専用レビューセッションを起動します。

通常のレビューリクエスト（「このコードをレビューして」）と比べ、`/ultrareview`は：

* 変更されたファイルを自動的に特定・読み込む
* バグ検出に特化したモードで動作する
* 設計的な問題（インターフェース設計・責務の分離など）もカバーする

### 使い方

Claude Codeのチャット欄で以下のように入力するだけです。

コマンドを実行すると、以下の手順が自動で行われます。

1. 最新のgit差分を読み込む
2. 変更ファイルの全コンテキストを取得する
3. 専用のバグ検出モードでレビューを実施する
4. 問題のある箇所を優先度付きでリスト化する

### 利用条件

公式情報によると、プランごとの無料利用回数は以下の通りです。

| プラン | 無料枠 |
| --- | --- |
| Pro | 初回3回（一度限り） |
| Max | 初回3回（一度限り） |
| Teams / Enterprise | 無料枠なし（使用ごとに課金） |

4回目以降（Pro/Max）および Teams/Enterprise プランの料金体系は[公式ページ](https://code.claude.com/docs/en/ultrareview)を参照してください。

### /ultrareviewが効果的な場面

```
✅ PRを作成する前の最終確認
✅ 大きなリファクタリング後の品質チェック
✅ 新機能追加時のエッジケース検出
✅ セキュリティ上の問題を含む可能性がある変更
```

---

## 4. モデル移行チェックリスト

Opus 4.7のリリースと同時に、旧モデルの非推奨化が発表されています。

| 非推奨モデル | 廃止日 | 移行先 |
| --- | --- | --- |
| `claude-sonnet-4-20250514` | 2026-06-15 | `claude-sonnet-4-6` |
| `claude-opus-4-20250514` | 2026-06-15 | `claude-opus-4-7` |

**移行チェックリスト:**

```
[ ] コードベース内の非推奨モデルIDを検索
    grep -r "claude-sonnet-4-20250514\|claude-opus-4-20250514" .

[ ] 移行先モデルIDに変更
    - claude-sonnet-4-20250514 → claude-sonnet-4-6
    - claude-opus-4-20250514  → claude-opus-4-7

[ ] ステージング環境でレスポンス品質を確認
[ ] 本番環境に適用（期限: 2026-06-15）
```

---

## 5. まとめ

Claude Opus 4.7とともに導入された3つの開発者向け機能を整理します。

| 機能 | 主な用途 | 今すぐ使えるか |
| --- | --- | --- |
| xhigh effort | 高精度推論が必要なAPIコール | ✅ GA済み |
| task budgets | 自律エージェントのコスト管理 | ✅ ベータ（本番利用可能） |
| /ultrareview | PR前のバグ検出 | ✅ Claude Code Pro/Max |

**特に注目したいのはtask budgets**です。自律型エージェントがツールを多用するユースケースでは、無制限のトークン消費がコスト上のリスクになります。20,000トークンから設定でき、モデルが予算内で最善策を選択する仕組みは、本番エージェントの運用コスト管理に直結します。

/ultrareviewはClaude Codeユーザーにとって即座に使えるバグ検出ツールです。PRを出す前の最終チェックとして組み込むと、レビュー工数の削減に貢献します。

---

## 参考リンク
