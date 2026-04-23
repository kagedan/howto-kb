---
id: "2026-04-07-複数aiエージェントが記憶を共有する中央メモリをsqlitemcpで実装した-01"
title: "複数AIエージェントが記憶を共有する「中央メモリ」をSQLite+MCPで実装した"
url: "https://zenn.dev/takawasi/articles/2251a734745f60"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "cowork", "zenn"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## はじめに

個人でAIサービス群を開発・運用していると、ある問題にぶつかる。

「Claude Code（CC）」「DeepSeek（DSC）」「Cowork（ブラウザ経由のレビュー担当）」——複数のAIエージェントがそれぞれ別のコンテキストで動いているとき、**誰が何を知っていて、何をやったのか**が散逸する。

gitのコミットログ？ あれは「何を変えたか」しか分からない。「なぜやったか」「次に何をすべきか」はそこにない。

この問題をSQLite + MCP（Model Context Protocol）で解決した話を書く。

## 構成

```
Cowork (Claude Desktop)
  ↕
MCP/SSE Bridge Server (Go + SQLite = 唯一の真実)
  ↕
HTTP API Runner (CC headless / DeepSeek) → タスク実行
```

核はBridge Server上のSQLiteひとつ。これが全エージェント共有の「中央メモリ」になる。

### なぜSQLiteか

* VPSのメモリが1.9GB。PostgreSQLを立てる余裕はない
* 書き込みは基本1エージェントずつ（同時書き込み競合が少ない）
* FTS5で全文検索が使える
* バックアップは`.db`ファイルをコピーするだけ

過剰な技術選定は試行機会の損失。動くものを最速で作るならSQLiteで十分だった。

## メモリの構造

SIの「層」構造をそのままSQLiteのレコードにマッピングしている。

```
layers/principles/principles.md             → 不変原則
layers/self/self.md                         → SIの自己定義
layers/ecosystem/ecosystem.md               → 全サービス状態
users/{user}/cassettes/{project}/M_layer.md → 作業記憶
users/{user}/cassettes/{project}/P_layer.md → プロジェクト定義
layers/principles/tasks/*.md                → タスクキュー
```

各レコードはバージョン番号を持ち、楽観的ロック（`expect_version`）で更新する。誰がいつ何を書いたかの履歴もすべて残る。

## MCPツール

Bridge ServerがMCPサーバーとして以下のツールを公開している。

| ツール | 役割 |
| --- | --- |
| `context_load` | ノード種別に応じた関連レイヤーを一括取得 |
| `memory_read` | 単一レイヤー読み取り |
| `memory_write` | バージョン付き書き込み |
| `memory_search` | FTS5全文検索 |
| `memory_list` | 全レイヤー一覧 |
| `runner_kick` | ランナー（CC/DSC）を即時起動 |

Cowork（Claude Desktop）からMCP経由で`memory_write`すると、その瞬間にBridge上のSQLiteが更新される。CC headlessから同じレイヤーを`memory_read`すれば最新の内容が読める。**ファイル同期もgit pullも不要**。

## 実際のワークフロー

今日やった作業がまさにこれだった。

1. **Cowork**がブラウザでVPSサービス群を巡回レビュー
2. 問題を発見（CreditGateのi18n未翻訳、ServicePortalのログイン状態不整合 等）
3. **Cowork**が`memory_write`でタスクファイルを中央メモリに投入
4. **Cowork**が`runner_kick`でCC(Sonnet)を起動
5. **CC**がタスクを拾って修正作業を開始

人間（自分）がやったのは「レビューしろ」と言っただけ。タスクの発見→記録→実行キックまでAIエージェント間で完結している。

## 所感

「AIに記憶を持たせる」というと大仰に聞こえるが、やったことは**SQLiteにMarkdownを保存してMCPで読み書きできるようにした**だけだ。

重要なのは技術の複雑さではなく「複数エージェントが同じ真実を見れる」という構造。これがないと、エージェントを増やすたびに情報の伝言ゲームが発生して破綻する。

個人開発でVPS1台・メモリ2GB未満でもこの構造は成立する。SQLiteは偉大。
