---
id: "2026-04-15-脱ragn8n-dify-で自社専用mcpサーバーを構築しclaude-codeに生きた情報を流し込-01"
title: "【脱・RAG】n8n × Dify で「自社専用MCPサーバー」を構築し、Claude Codeに生きた情報を流し込む技術"
url: "https://qiita.com/YushiYamamoto/items/62075ffdf312fa9c38a6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

[![A_futuristic_conceptual_202604152238.jpeg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637864%2F48501e57-b38c-4f01-809e-9dfb62f2af29.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0ffabc2043f5e97dbd5ca8cc0d65515f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3637864%2F48501e57-b38c-4f01-809e-9dfb62f2af29.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0ffabc2043f5e97dbd5ca8cc0d65515f)

## 1. RAGの限界と「Live Context API」への転換

従来のRAG（検索拡張生成）は、静的なベクターDBに依存するため情報の「鮮度」が低く、かつ「参照のみ」でアクション（実行）ができないという致命的な欠陥がありました。  
Anthropicが提唱した **Model Context Protocol (MCP)** は、AIモデルを組織の動的データと「接続」する標準規格です。本アーキテクチャでは、**n8nをMCPトランスポート層（手足）、Difyを情報の精製レイヤー（フィルター）** として配置し、Claude Codeに組織の「今」をセキュアに注入します。

### 全体アーキテクチャ図（非同期・高レジリエンス設計）

---

## 2. 堅牢性と安全性を担保する「4つの技術要件」の実装

AIエージェントを実務に投入する際、プロトコルの制約を無視した設計は「Gateway Timeout」や「データ破損」を招きます。以下の実装を強制します。

### ① 非同期HITL（Human-in-the-Loop）の設計

n8nのMCP実装では、`Wait`ノードを用いた同期的な承認待機は動作しません。接続のタイムアウトを防ぐため、書き込み操作は即座に受理ステータスを返し、プロセスを非同期化します。

**書き込み系アクションのレスポンス型定義（TypeScript）**

```
/**
 * 破壊的変更（Write）に対する即時受理レスポンス
 */
interface McpAsyncAcceptedResponse {
  status: "accepted";
  request_id: string; // 追跡用UUID
  acknowledgement: string; // AIがユーザーに表示するメッセージ
  approval_metadata: {
    target_approver: string; // 承認権限者
    status_url: string; // 進捗確認用のダッシュボードURL
  };
}
```

### ② 「30秒の壁」を突破する計算資源の再配置

CLIクライアントは通常30〜60秒でタイムアウトします。Difyでの重厚な推論や多段連携をn8n側で待機させないため、\*\*「n8nは搬送、Claudeは思考」\*\*に責務を分離します。

* **n8n/Difyの責務**: SaaS APIからデータを高速取得し、不要なメタデータやHTMLタグの剪定（Context Pruning）に徹する。
* **Claude Codeの責務**: 取得した膨大な生コンテキストを自身の長文脈ウィンドウに取り込み、モデル内部で構造化と最終推論を行う。

### ③ 自己修復（Self-Correction）を実現するエラー設計

APIエラー（500）発生時にAIが思考停止するのを防ぐため、エラーを「指示」に変換して返却します。

**エラー返却用JSON Schema**

```
{
  "type": "object",
  "properties": {
    "isError": { "const": true },
    "errorCode": { "type": "string" },
    "valid_parameters": { "type": "array", "items": { "type": "string" } },
    "instruction_for_ai": {
      "type": "string",
      "description": "AIが次に取るべき修復アクション（例：プロジェクトIDを'DEV'に修正して再実行せよ）"
    }
  },
  "required": ["isError", "errorCode", "instruction_for_ai"]
}
```

---

## 3. 安全性：Naked MCPサーバーの防御設計

認証のないMCPサーバーは社内資産へのバックドアとなります。物理的な安全性を確保するため、以下の多層防御を実装します。

1. **認証ヘッダーの強制**: n8nの `MCP Server Trigger` において、HeaderベースのAPIキー認証を必須化。
2. **ゼロトラスト接続**: エンドポイントを公開せず、`Tailscale` 等のメッシュVPN、あるいは `Cloudflare Tunnel` を用い、認可された開発端末からのVPN経由アクセスのみを許可。
3. **認可（RBAC）**: n8nのワークフロー内で実行ユーザーのIDを検証し、対象プロジェクトへの操作権限をAPI実行直前に再チェック。

### Claude Code 接続設定 (`claude_desktop_config.json`)

```
{
  "mcpServers": {
    "corp-intel-gateway": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-http", "--url", "https://n8n.internal.example.com/rest/mcp"],
      "env": {
        "X_N8N_API_KEY": "YOUR_SECURE_API_KEY"
      }
    }
  }
}
```

---

## 4. 実装ツール定義：コンテキスト取得（Read専用）

n8n側で定義する、AIが呼び出し可能なツール定義の例です。

```
{
  "name": "get_project_live_context",
  "description": "Slackの最新議論とJiraのステータスを統合したコンテキストを返します。Read専用アクションです。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "project_id": {
        "type": "string",
        "description": "Jiraプロジェクトキー（例: AI-PLAT）"
      },
      "lookback_window": {
        "type": "string",
        "enum": ["1h", "24h", "7d"],
        "default": "24h"
      }
    },
    "required": ["project_id"]
  }
}
```

---

## 5. 結論：AIを「組織の神経系」へ

本構成の導入により、開発者はターミナルを一歩も出ることなく、以下のワークフローを安全かつ低遅延に実現できます。

1. **Read**: `claude "昨日のSlack議論を反映して、auth.tsのリファクタリング案を出して"`  
   → n8nがDify経由で最新ログを注入し、Claudeがその場で回答。
2. **Write**: `claude "Jiraチケット PROJ-101 をDoneに更新して"`  
   → n8nが「受理」を返し、裏でPMのSlackに承認依頼を送信。

「生きた情報」をMCP経由で流し込む仕組みは、AIを単なるチャットボットから、**現場の規律を守りつつ並走する最強の軍師**へと進化させます。

---

**この記事を書いた人✏️[@YushiYamamoto](/YushiYamamoto "YushiYamamoto")**  
株式会社プロドウガ CEO / AIアーキテクト  
Next.js / TypeScript / n8nを活用した自律型アーキテクチャ設計を専門としています。  
日々の自動化の検証結果や、ビジネス側の視点（ROI等）に関するより深い考察は、以下の公式サイトおよびnoteで発信しています。
