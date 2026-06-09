---
id: "2026-06-08-codex-cli-最新アップデートガイド-realtime-v2mcp強化モデル移行2026年4月-01"
title: "Codex CLI 最新アップデートガイド — Realtime V2・MCP強化・モデル移行（2026年4月）"
url: "https://zenn.dev/kai_kou/articles/229-codex-cli-0120-mcp-realtime-v2-guide"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月、OpenAIのCodex CLIに大規模なアップデートが届きました。v0.119.0（4月10日）とv0.120.0（4月11日）の2リリースで、**Realtime Voice V2**・**MCP機能の大幅強化**・**リモートワークフロー改善**が一気に実装されました。

さらに2026年4月14日（本日）をもって、ChatGPT連携時の旧モデル（`gpt-5.1`系、`gpt-5.2-codex`）がCodexから削除されます。

この記事では、公式チェンジログをもとに、各アップデートの内容と移行手順を解説します。

### この記事で学べること

* Codex CLI v0.119.0 / v0.120.0 の主要変更点
* Realtime Voice V2（WebRTC）の新しい動作
* MCP強化（リソース読み取り・エリシテーション・ファイルアップロード）
* リモートワークフロー（`codex exec-server`）の概要
* モデル移行ガイド（gpt-5.1系 → gpt-5.4系）

### 対象読者

* Codex CLIを開発ワークフローで利用しているエンジニア
* MCPサーバーをCodexと組み合わせている開発者
* Codex CLIの最新動向を追っている方

### 前提環境

* Node.js v22.x 以上
* Codex CLI 最新版（v0.120.0を推奨）

```
# 最新バージョンへの更新
npm install -g @openai/codex@latest
```

---

## TL;DR

* **v0.119.0（4/10）**: Realtime Voice V2がデフォルト化、MCP resource reads・file-parameter uploads対応、egress WebSocket追加
* **v0.120.0（4/11）**: Realtime V2でバックグラウンドエージェント進捗ストリーミング、MCP outputSchema対応
* **4/14**: `gpt-5.1`系・`gpt-5.2-codex`がChatGPT連携から削除 → `gpt-5.4` または `gpt-5.3-codex` に移行

---

## v0.119.0（2026年4月10日）の主要変更

### 1. Realtime Voice V2: WebRTCがデフォルトに

Codex CLIのリアルタイム音声セッションが、**v2 WebRTCパスをデフォルト**として使用するようになりました。

主な改善点：

| 機能 | 内容 |
| --- | --- |
| トランスポート設定 | WebRTC（デフォルト）またはWebSocketを選択可能 |
| 音声選択 | セッションごとに音声を設定可能 |
| TUIメディアサポート | ターミナルUI上でネイティブメディア操作 |
| アプリサーバー対応 | app-serverフローでもv2に対応 |

設定例（`config.toml`）：

```
[realtime]
transport = "webrtc"  # "webrtc" または "websocket"
voice = "alloy"       # alloy, echo, fable, onyx, nova, shimmer
```

### 2. MCP強化: リソース読み取り・エリシテーション・ファイルアップロード

MCPサーバーとの連携機能が大幅に拡張されました。

**新機能一覧：**

```
MCP Apps / カスタムMCPサーバーで利用可能になった機能:
├── resource reads（リソース読み取り）
├── tool-call metadata（ツール呼び出しメタデータ）
├── custom-server tool search（カスタムサーバーのツール検索）
├── server-driven elicitations（サーバー主導型エリシテーション）
├── file-parameter uploads（ファイルパラメータのアップロード）
└── plugin cache refreshes（プラグインキャッシュの改善）
```

**特に注目: server-driven elicitations**

MCP仕様の[エリシテーション（Elicitation）](https://modelcontextprotocol.io/docs/concepts/elicitation)は、MCPサーバーがクライアント（この場合Codex CLI）に対して追加の入力情報を要求する仕組みです。これにより、MCPサーバーが不足情報を動的に収集するインタラクティブなフローが実現します。

**ファイルアップロードの活用例：**

```
// MCPツール定義でファイルパラメータを受け付ける例
{
  "name": "analyze_code",
  "description": "コードファイルを解析する",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file": {
        "type": "string",
        "format": "binary"
      }
    }
  }
}
```

**起動時のパフォーマンス改善：**

* ハイフン入りサーバー名でのツール一覧表示が正常化
* `/mcp` コマンドが全ツールの事前スキャンを省略（高速化）
* 無効化されたサーバーの認証プローブをスキップ
* residencyヘッダーを `codex mcp-server` が正しく認識

### 3. リモートワークフロー: egress WebSocket・exec-server

リモート/アプリサーバー環境向けの機能が強化されました。

**新機能：**

```
# 実験的なexec-serverサブコマンド
codex exec-server --port 8080

# リモートCDフォワーディング
codex --remote wss://your-server.example.com --cd /path/to/project

# egress WebSocketトランスポート
# （app-serverクライアントがWebSocket経由でサンドボックスと通信）
```

**サンドボックス改善：**

* Windowsでプロキシ限定ネットワーキングをOS層で強制可能（環境変数依存から脱却）
* `sandbox-aware` ファイルシステムAPIの追加

### 4. TUI改善

* **`Ctrl+O`** でコピー機能を追加（クリップボード動作も改善）
* **`/resume`** コマンドでセッションIDや名前を指定して直接ジャンプ可能

```
# セッション名やIDで直接再開
/resume my-session-name
/resume ses_abc123
```

---

## v0.120.0（2026年4月11日）の主要変更

### 1. Realtime V2: バックグラウンド進捗ストリーミング

Realtime V2がさらに強化され、**バックグラウンドで動作中のエージェントの進捗をストリーミング**できるようになりました。

* エージェントが処理中でも、完了を待たずに進捗を音声/テキストで確認可能
* フォローアップレスポンスをキューに積んで、アクティブなレスポンス完了後に順次処理

```
[Agent processing...]
> ストリーミング進捗: ファイルを解析中... (3/10)
> ストリーミング進捗: テストを実行中... (7/10)
[Agent done] → フォローアップをキューから実行
```

### 2. MCP outputSchema: 構造化ツール結果の型付け

コードモードのツール宣言に\*\*`MCP outputSchema` 詳細\*\*が追加されました。

```
// ツール定義にoutputSchemaを追加
{
  "name": "get_test_results",
  "description": "テスト結果を取得",
  "outputSchema": {
    "type": "object",
    "properties": {
      "passed": { "type": "integer" },
      "failed": { "type": "integer" },
      "errors": {
        "type": "array",
        "items": { "type": "string" }
      }
    }
  }
}
```

これにより、MCPツールの戻り値が型付けされ、Codexがより正確に結果を解釈できるようになります。

### 3. Hook改善

**SessionStartフックの強化：**

`/clear`で作成されたセッションと、新規セッション・再開セッションを区別できるようになりました。

```
# .claude/hooks/session-start.sh の例
#!/bin/bash
if [ "$CODEX_SESSION_SOURCE" = "clear" ]; then
  echo "クリア後の新セッション"
else
  echo "新規または再開セッション"
fi
```

**フックアクティビティ表示の改善：**

* 実行中のフックと完了済みフックがTUI上で分けて表示
* 完了済みフックの出力は有用な場合のみ保持

---

## モデル移行ガイド（2026年4月14日）

本日2026年4月14日をもって、ChatGPT連携時のCodexで以下のモデルが使用不可になります。

### 削除されるモデル

| モデル | 削除日 |
| --- | --- |
| `gpt-5.2-codex` | 2026-04-14 |
| `gpt-5.1-codex-mini` | 2026-04-14 |
| `gpt-5.1-codex-max` | 2026-04-14 |
| `gpt-5.1-codex` | 2026-04-14 |
| `gpt-5.1` | 2026-04-14 |
| `gpt-5` | 2026-04-14 |

### 利用可能なモデル（移行先）

| モデル | 特徴 | 推奨用途 |
| --- | --- | --- |
| `gpt-5.4` | 旗艦モデル。コーディング・推論・エージェント全方位最強 | 複雑なタスク全般 |
| `gpt-5.4-mini` | 高速・コスト効率。レスポンシブなコーディング | 短いタスク・サブエージェント |
| `gpt-5.3-codex` | コーディング特化。複雑なSWEに最適 | 大規模コードベース向け |
| `gpt-5.3-codex-spark` | リアルタイム反復（Pro限定） | ペアプログラミング的な利用 |
| `gpt-5.2` | 前世代汎用モデル | APIキー利用時の互換維持 |

### 移行手順

**1. `config.toml`を更新する**

```
# 旧設定（削除対象）
# model = "gpt-5.1-codex"

# 新設定（推奨）
model = "gpt-5.4"
```

**2. コマンドラインで指定している場合**

```
# 旧
codex --model gpt-5.1-codex "タスクの説明"

# 新
codex --model gpt-5.4 "タスクの説明"
```

**3. セッション内で切り替える**

> **注意:** APIキーを使ってCodexにサインインしている場合（ChatGPT連携ではない場合）は、Chat Completions/Responses API互換のモデルを引き続き利用できます。

---

## 注意点

**`gpt-5.4` への移行後の留意事項：**

* モデル変更後はベンチマークや出力品質が変わる可能性があります。既存のプロンプトを再調整することが推奨されます
* [Codex Models公式ページ](https://developers.openai.com/codex/models)で最新の対応状況を確認してください

**MCP elicitation利用時：**

* MCP Elicitation仕様はまだ発展途上です。サーバー実装によって動作が異なる場合があります
* 詳細は[MCP仕様書](https://modelcontextprotocol.io/docs/concepts/elicitation)を参照してください

---

## まとめ

2026年4月のCodex CLI（v0.119.0 / v0.120.0）では、以下の改善が実施されました：

* **Realtime Voice V2**: WebRTCがデフォルト化、バックグラウンド進捗ストリーミング対応
* **MCP強化**: resource reads・server-driven elicitations・file-parameter uploads・outputSchema対応で、MCPサーバーとの連携が大幅に充実
* **リモートワークフロー**: `codex exec-server`、egress WebSocket、サンドボックス対応ファイルシステムAPIで、リモート・CI環境での利用が拡大
* **モデル移行**: 2026年4月14日に`gpt-5.1`系を削除。`gpt-5.4` または `gpt-5.3-codex` への移行が必要

定期的に `npm install -g @openai/codex@latest` でアップデートを適用し、最新機能を活用してください。

---

## 参考リンク
