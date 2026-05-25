---
id: "2026-05-24-codex-app-server-とは何か-自プロダクトに-ai-コーディングエージェントを埋め込む-01"
title: "Codex App Server とは何か — 自プロダクトに AI コーディングエージェントを埋め込む新しい選択肢"
url: "https://zenn.dev/shintaroamaike/articles/4d69e695902992"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "GPT"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

<https://developers.openai.com/codex/app-server>

---

## はじめに

OpenAI の Codex は、もはや単なる「コード補完ツール」ではない。かつての Codex モデル（code-davinci-002 等）とは別物であり、現在は GPT-4o を始めとする最新モデルを活用したフル機能のコーディングエージェント基盤を指す。VS Code 拡張や Web UI を通じて、リポジトリを横断的に理解し、テストを書き、PR を作成するところまで担えるようになった。

その Codex を **自社プロダクトに深く組み込む**ためのインターフェースが、今回取り上げる **Codex App Server** だ。

VS Code 拡張自体もこのプロトコルで動いており、実装はオープンソース（[openai/codex](https://github.com/openai/codex/tree/main/codex-rs/app-server)）として公開されている。「どこまで自前でコントロールできるか」を突き詰めたいエンジニアにとって、見逃せない選択肢となっている。

---

## Codex App Server の立ち位置

OpenAI が提供する Codex の利用経路は大きく 3 つある。

| 手段 | 用途 |
| --- | --- |
| **Codex SDK** | CI・自動化・非インタラクティブな実行 |
| **Codex CLI** | ターミナル上でのインタラクティブ操作 |
| **Codex App Server** | 自社プロダクトへの深い埋め込み（カスタム UI・IDE 拡張など） |

App Server は「深い統合」のための選択肢だ。認証フロー、会話履歴の管理、コマンド実行の承認 UI、ストリーミングイベントのハンドリング——これらをすべて自前で制御したい場合に使う。

---

## プロトコルの設計思想

App Server は **JSON-RPC 2.0** をベースにした双方向通信プロトコルを採用している。[MCP（Model Context Protocol）](https://modelcontextprotocol.io/) と同じ設計哲学を持ち、リクエスト・レスポンスとサーバー発のノーティフィケーションが混在する非同期モデルで動く。

メッセージは 3 種類に分類される。

* **リクエスト** — `method`・`params`・`id` を持つ。クライアントからサーバーへ送る。
* **レスポンス** — `id` を echo し `result` または `error` を返す。
* **ノーティフィケーション** — `id` を持たないサーバー起点のメッセージ。イベントの通知に使われる。

### トランスポート

| トランスポート | 状態 | 用途 |
| --- | --- | --- |
| `stdio` | 安定版 | サブプロセスとして起動し、親プロセスと pipe でやり取り |
| `websocket` | 実験的 | ローカルホスト経由・SSH ポートフォワーディング |

WebSocket モードを外部に公開する場合は認証設定が必須で、capability token または署名付きベアラートークンをサポートする。**本番では loopback 以外への非認証公開は厳禁。**

TypeScript 型定義や JSON Schema は CLI から自動生成でき、実装するバージョンに完全に追従した型が手に入る。詳細は[公式ドキュメント — Getting started](https://developers.openai.com/codex/app-server#getting-started) を参照。

---

## コアコンセプト — Thread / Turn / Item

App Server の設計は 3 つの概念で構成される。

### Thread

会話のライフサイクル全体を管理するコンテナ。`thread/start` で新規作成、`thread/resume` で再開、`thread/fork` で分岐できる。会話履歴は JSONL としてディスクに永続化される。

### Turn

1 つのユーザー入力とそれに続くエージェントの作業単位。ターン開始後は `turn/started` ノーティフィケーションが届き、完了時に `turn/completed` が来る。処理中に `turn/steer` を送ることで、実行中のターンに追加指示を差し込むことも可能だ。

### Item

ターン内での具体的な処理単位。コマンド実行・ファイル変更・ツール呼び出しなど多様な型があり、それぞれ `item/started` → (delta) → `item/completed` のライフサイクルで流れてくる。

---

## 接続からターン開始までのフロー

実際のセッション確立は以下のシーケンスに従う。

`initialize` → `initialized` のハンドシェイクは必須で接続ごとに 1 回のみ。これを省略すると以降のすべてのリクエストが `Not initialized` エラーになる。

---

## 承認フロー — ユーザーに確認を挟む

App Server の重要な機能の一つが **承認（Approval）** の仕組みだ。コマンド実行やファイル変更が発生する前に、クライアントへ確認リクエストが届く。これにより、**危険な操作をユーザーが明示的に承認する UI** をプロダクト側で自由に設計できる。

承認ポリシーはターン単位で設定でき、CI では全自動化（`approvalPolicy: "never"`）、開発ツールでは危険なコマンドだけ確認（`"unlessTrusted"`）といった使い分けが可能だ。

ファイル変更の承認フローも同様の構造を持つ。詳細は[公式ドキュメント — Approvals](https://developers.openai.com/codex/app-server#approvals) を参照。

---

## サンドボックスポリシー

実行環境の権限をターンごとに制御できる。設定可能なポリシーは以下の通り。

| ポリシー | 内容 |
| --- | --- |
| `readOnly` | 読み取り専用。ファイル変更・コマンド実行は不可 |
| `workspaceWrite` | 指定したルートディレクトリへの書き込みのみ許可。指定ディレクトリ外へのアクセスは制限される |
| `externalSandbox` | コンテナ等で外部隔離済みの環境向け。App Server 自身のサンドボックスをスキップ |
| `dangerFullAccess` | 制限なし。CI など信頼できる環境限定 |

`sandboxPolicy` はターン単位で上書きでき、後続ターンのデフォルトにもなる。各ポリシーの詳細な設定項目（`writableRoots`・`networkAccess`・`readOnlyAccess` 等）は[公式ドキュメント — Sandbox read access](https://developers.openai.com/codex/app-server#sandbox-read-access-readonlyaccess) を参照。

---

## Skills と Apps（コネクター）

### Skills

`SKILL.md` として定義された手順書を Codex に読み込ませる仕組み。テキスト入力に `$skill-name` を含め、`skill` タイプの input item と組み合わせることで呼び出せる。`skills/list` で利用可能なスキルを列挙でき、`skills/changed` ノーティフィケーションでファイル変更を検知できる。詳細は[公式ドキュメント — Skills](https://developers.openai.com/codex/app-server#skills) を参照。

### Apps（コネクター）

Gmail・Google Drive・Asana といった外部サービスとの連携。`app/list` で利用可能なコネクターを取得し、`$app-slug` でターンから呼び出す。MCP サーバーをベースにしており、ツール実行前に承認フローを経由する。詳細は[公式ドキュメント — Apps](https://developers.openai.com/codex/app-server#apps-connectors) を参照。

---

## Codex SDK との使い分け

|  | Codex SDK | Codex App Server |
| --- | --- | --- |
| **主な用途** | CI・バッチ・スクリプト | カスタム UI・IDE 拡張・製品組み込み |
| **インタラクション** | 非インタラクティブ | 双方向リアルタイム |
| **会話継続** | 限定的 | Thread / Turn で完全管理 |
| **承認フロー** | なし | あり（クライアントが実装） |
| **ストリーミング** | 基本的なもの | 詳細なイベント全種 |
| **認証管理** | API キー中心 | API キー / ChatGPT OAuth / 外部トークン |

一言で言えば、**「エージェントを操作する UI を自分で作りたいなら App Server、とにかくジョブを流したいなら SDK」** だ。

---

## 実装時の注意点

### 1. `initialize` ハンドシェイクは必須かつ 1 回限り

接続ごとに `initialize` → `initialized` を最初に送ること。2 回送ると `Already initialized` エラーになる。

### 2. 実験的 API は明示的にオプトイン

一部のメソッドや動的ツール呼び出しは `capabilities.experimentalApi: true` が必要。本番利用前にドキュメントの成熟度を必ず確認する。[Feature Maturity](https://developers.openai.com/codex/feature-maturity) は各機能の安定度（beta / stable / deprecated 等）を一覧で確認できる公式リソースであり、エンタープライズ利用を検討する場合は特に重要な判断材料になる。

### 3. WebSocket の認証設定を怠らない

ループバック以外への公開は**デフォルトで無認証**。`--ws-auth` フラグで必ずトークン認証を設定すること。ファイルベースのトークン（`--ws-token-file`）を推奨する。

### 4. ノーティフィケーションの取捨選択

`item/agentMessage/delta` のような高頻度なノーティフィケーションは、`initialize` 時に `optOutNotificationMethods` で抑制できる。クライアントの処理負荷とのバランスを取ること。

### 5. `clientInfo.name` はエンタープライズ利用の識別子になる

`clientInfo.name` は OpenAI の Compliance Logs Platform でクライアントを識別するために使われる。エンタープライズ向け統合を構築する場合は OpenAI への登録を検討する。

---

## いつ Codex App Server を選ぶか

Codex App Server はあらゆるケースに適した選択肢ではない。「AI エージェント機能をプロダクトに追加したい」という出発点から、自然に検討される代替手段と何が違うのかを整理することで、採用判断の基準が見えてくる。

### 意思決定フロー

---

### 代替手段との違い

#### 「既製の CLI ツールをそのまま使う」との違い

Claude Code に代表される CLI ツールは、**開発者個人の生産性を高める**ために設計されたプロダクトだ。ターミナル上で動作し、承認フローや UI はツール側が提供する。

Codex App Server はそれとは根本的に立ち位置が異なる。**プロダクトを作るためのプロトコル**であり、UI・認証・承認フローをどう見せるかはすべて実装する側の設計に委ねられている。

既製ツールで解決できるなら無理に App Server を選ぶ必要はない。「自社のブランドや UX に合わせたい」「ユーザーの操作ログを自社で管理したい」といった要件が出てきたとき、初めて App Server が候補に上がる。

#### 「API を直接呼び出す」との違い

OpenAI API や Anthropic API を直接呼ぶアプローチは、シンプルな用途には十分だ。しかしエージェント的な機能——コマンド実行・ファイル変更・長時間タスク・中断と再開——が絡み始めると、クライアント側に以下の実装が積み重なっていく。

Codex App Server はこれらの複雑さをプロトコルレベルで吸収している。Thread による会話の永続化・承認フローのイベント設計・サンドボックスポリシーの管理がサーバー側で完結し、クライアントはイベントを受け取って UI に反映することに集中できる。

---

### ビジネス観点：有効なシーン

| シーン | App Server が有効な理由 |
| --- | --- |
| **SaaS にコーディングエージェントを内蔵する** | UI・ブランディング・認証を完全に自社でコントロールでき、差別化機能として成立する |
| **社内開発者向けポータルの構築** | 承認フロー・監査ログ・権限管理を社内ポリシーに合わせて実装できる |
| **エンタープライズ向けデベロッパープラットフォーム** | SSO 連携・コンプライアンス要件への対応を実装層で制御できる |
| **コードレビュー・PR 作成を自動化するワークフロー基盤** | 会話の分岐（`thread/fork`）や再開（`thread/resume`）を活用した複雑なフローを構築できる |

一方、以下のシーンでは App Server を選ぶ必要はない。

| シーン | より適した選択肢 |
| --- | --- |
| 開発チームの生産性向上ツールの導入 | 既製の CLI ツール・IDE 拡張 |
| 既存サービスへの AI 機能の軽量追加 | API 直接呼び出し |
| CI / CD パイプラインでの非インタラクティブ実行 | Codex SDK |

---

### エンジニア観点：採用前に確認すべきこと

App Server の採用はプロトコルレベルの統合を意味する。以下を事前に確認しておきたい。

**実装コストの見積もり**  
UI・承認フロー・エラーハンドリング・認証フローはすべて自前実装になる。既製ツールを使う場合と比べて初期開発コストは大きい。

**非同期・イベントドリブン設計への対応**  
ストリーミングノーティフィケーションを処理するアーキテクチャが必要になる。同期的な API 呼び出しに慣れたチームには設計の転換が求められる。

**ベンダーロックインの評価**  
App Server のプロトコルは OpenAI Codex に固有のものであり、他のエージェント基盤への移行は容易ではない。長期的な技術選定として許容できるかを組織として判断する必要がある。

**実験的 API の成熟度管理**  
一部の機能は実験的ステータスにある。本番で利用する機能は [Feature Maturity](https://developers.openai.com/codex/feature-maturity) を確認し、安定版のみに絞ることを推奨する。

---

## まとめ

Codex App Server は、AI コーディングエージェントを「ツールとして使う」段階から「プロダクトに組み込む」段階へ進むためのインターフェースだ。

* JSON-RPC 2.0 ベースの明確なプロトコル設計
* Thread / Turn / Item による細粒度な会話管理
* 承認フローとサンドボックスによる安全な実行制御
* Skills と Apps による拡張性

VS Code 拡張そのものがこのプロトコルで動いているという事実は、実装の信頼性を裏付けている。自社の開発ツールや SaaS プロダクトに Codex の能力を深く統合したいなら、まずこのプロトコルの理解から始めることを強くすすめる。

---

## 参考リンク
