---
id: "2026-06-23-shintaro-campon-httpstcolfb7urvjje-01"
title: "@shintaro_campon: https://t.co/lfB7uRVJJE"
url: "https://x.com/shintaro_campon/status/2069541456692527553"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "OpenAI", "GPT", "x"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

https://t.co/lfB7uRVJJE


--- Article ---
## 開発環境が「AIチャット」から「統合プラットフォーム」へ進化した

Cursor 3.8がリリースされた。今回のアップデートでAI開発環境は単一モデルの利用からワークフローの統合プラットフォームへと移行する。

これまで開発者はChatGPTやClaudeの画面を行き来してコードをコピペしていた。これからは開発資産やルール、外部ツールを接続するカスタマイズ可能なハブが開発の基盤となる。

MCP（Model Context Protocol）への対応が本格化した。これはAIに自社の開発プロセスを接続する段階への突入を意味する。

![](https://pbs.twimg.com/media/HLh8uVybkAAwoVp.jpg)

## 業界全体で進む「統合」という動き

Cursor、OpenAI、Adobeはユーザーのワークフローを自社プラットフォーム内に集約する方向で動いている。

Cursor 3.8のCustomizeページは司令塔として機能する。プラグイン、スキル、MCP、サブエージェント、ルール、コマンド、フックを一括管理できる。

チーム内での人気ランキング（リーダーボード）も実装された。GitLab、BitBucket、Azure DevOpsのリポジトリからプラグインを直接インポートできる。

OpenAIはChatGPTアプリ、Codex、AIブラウザのAtlasを一つのデスクトップ・スーパーアプリに統合する計画を進める。製品の断片化による質の低下を防ぐ狙いがある。

Adobe Fireflyは自社モデルに加え、Google、Runway、OpenAIを含む30以上のAIモデルを一つの環境に統合した。10枚から30枚の画像で独自のビジュアルスタイルを学習させる機能も追加された。

![](https://pbs.twimg.com/media/HLh8wQ4b0AA7oUW.png)

> OpenAIのアプリ統合はブラウザとアプリを行き来するストレスを減らす動きだ。CursorがMCPで外部ツールを飲み込み、OpenAIが自社ツールを統合する。僕らの作業コンテキストをどこが握るかの奪い合いだ。

## 開発者の視点：MCP連携がもたらす変化

Cursor 3.8の核はMCPの全面採用だ。これまでのAIエージェントはエディタ内のファイルやブラウザ検索に限定されていた。

MCPを使えばAIはデータベース、APIドキュメント、Issue管理ツール、Slackを直接参照できる。Atlassian Canvasのプラグインを使えばCursorの中からリアルタイムでプロジェクトの課題やドキュメントを確認可能だ。

ThreadPostのようなSaaS開発において、DBのスキーマやAPI仕様書をプロンプトに貼り付ける作業は不要になる。MCPサーバーを接続すればAIは常に最新の仕様を理解した状態でコードを提案する。

開発者はAIに知識を与える作業から解放され、AIと一緒に「どう作るか」を考える作業に集中できる。Adobeの事例にあるマルチモデルの統合もIDEの標準となる。

![](https://pbs.twimg.com/media/HLh8yJya4AA2FYA.png)

自分のPC内のローカルデータや社内ツールをAIが知っている状態にできるかどうか。これができる環境とできない環境ではアウトプットに差が出る。CursorのMCP対応は正しい進化だ。

![](https://pbs.twimg.com/media/HLh80RYasAAVVjE.jpg)

## 実務への影響：接続の技術

AIを自分の環境に接続する準備が必要だ。以下の3つのアクションが重要になる。

1. MCPサーバーの活用と構築
GitHub連携、Google Drive連携、PostgreSQL連携などをCursorに接続する。自社独自のAPIがあるならMCPサーバーを自作して接続する。

1. 「ルール」と「スキル」の資産化
Cursor 3.8ではプロジェクトごとのルール（.cursorrules）や特定のタスクを実行するためのスキルをチームで共有できる。暗黙の了解をコードとして言語化し、AIに守らせる。

1. マルチモデル戦略への移行
タスクに応じて最適なモデルを使い分ける。Adobeが30以上のモデルを統合したように、用途別の最適モデルを自分の中に持っておく。

今後はAIにコードを書かせる能力よりも、AIに自社のコンテキストをどう繋ぎ込むかという設計能力がエンジニアの価値を左右する。

![](https://pbs.twi
