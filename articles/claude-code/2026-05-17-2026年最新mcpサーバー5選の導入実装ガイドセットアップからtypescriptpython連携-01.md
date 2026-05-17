---
id: "2026-05-17-2026年最新mcpサーバー5選の導入実装ガイドセットアップからtypescriptpython連携-01"
title: "【2026年最新】MCPサーバー5選の導入・実装ガイド｜セットアップからTypeScript/Python連携まで徹底解説"
url: "https://qiita.com/sescore/items/3e4a86e275574f9902e8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "VSCode", "Python"]
date_published: "2026-05-17"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

## はじめに：MCPサーバーを「使える」状態にするまでの完全ガイド

2026年5月現在、MCP（Model Context Protocol）はAIエージェント開発における事実上の標準プロトコルです。しかし、「どのMCPサーバーを選ぶべきか」だけでなく、「実際にどう実装・連携するか」まで踏み込んだ情報はまだ不足しています。

本記事では、実務で特に利用価値の高い5つのMCPサーバーについて、**Tier分類による優先度判定**に加え、**実際に動くコードサンプル**と**セットアップ手順**を提供します。

### 対象読者

- Claude Code、Cursor、Windsurf等のAIエディタを日常的に使うエンジニア
- MCPサーバーを自前のアプリケーションから呼び出したい開発者
- AIエージェントの開発環境を整備したいテックリード
- TypeScript/Pythonでの実装パターンを知りたい方

### 対象MCPサーバー

| # | ツール名 | カテゴリ | 提供元 |
|---|----------|----------|--------|
| 1 | Context7 | ドキュメント参照 | Upstash |
| 2 | Playwright MCP | ブラウザ自動化 | Microsoft |
| 3 | PostgreSQL MCP | データベース操作 | Anthropic公式 |
| 4 | Sentry MCP | エラー監視連携 | Sentry |
| 5 | Firecrawl | Webスクレイピング | Firecrawl |

---

## 評価基準とTier分類

以下の5軸で各ツールを評価し、総合スコアでTier分類を行いました。

| 評価軸 | 説明 | 重み |
|--------|------|------|
| **実用性** | 日常の開発フローでの使用頻度 | 30% |
| **安定性** | プロダクション利用への耐性 | 25% |
| **セットアップ容易性** | 導入の手軽さ | 20% |
| **エコシステム** | 対応クライアント・コミュニティの充実度 | 15% |
| **独自性** | 他ツールで代替困難か | 10% |

### Tier定義

| Tier | 定義 | 該当ツール |
|------|------|------------|
| **Tier 1（必須級）** | 費用対効果が圧倒的。入れない理由がない | Context7, Playwright MCP, PostgreSQL MCP |
| **Tier 2（推奨）** | 特定ワークフローで大きな生産性向上 | Sentry MCP, Firecrawl |
| **Tier 3（選択型）** | ユースケース次第 | GitHub MCP, Slack MCP, Memory MCP等 |

---

## 環境準備：MCPクライアントの基本設定

まず、MCPサーバーを利用するためのクライアント側設定を整理します。

### Claude Codeの場合

Claude Codeでは `~/.claude/settings.json` にMCPサーバー設定を記述します。

```bash
# Claude Codeのバージョン確認
claude --version

# settings.jsonの場所を確認
ls ~/.claude/settings.json

# 設定ファイルがなければ作成
mkdir -p ~/.claude && touch ~/.claude/settings.json
```

### Cursorの場合

プロジェクトルートに `.cursor/mcp.json` を配置します。

### VS Code (GitHub Copilot) の場合

`.vscode/mcp.json` に記述します。

---

## Tier 1: Context7 — 最新ドキュメントをLLMに直接注入

### なぜTier 1なのか

LLMの学習データカットオフ問題を根本的に解決します。Next.js 15、Remix v3、Hono v4など、最新フレームワークのAPIを正確に参照できるようになります。APIキー不要・無料で使える点も大きなメリットです。

### セットアップ

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

### TypeScriptからMCPクライアントとして接続する実装例

MCPサーバーを自前のアプリケーションから呼び出す場合、`@modelcontextprotocol/sdk` を使用します。

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function queryContext7(libraryName: string, topic: string) {
  // MCPクライアントの初期化
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["-y", "@upstash/context7-mcp@latest"],
  });

  const client = new Client(
    { name: "my-app", version: "1.0.0" },
    { capabilities: {} }
  );

  await client.connect(transport);

  // 利用可能なツール一覧を取得
  const tools = await client.listTools();
  console.log("Available tools:", tools.tools.map(t => t.name));

  // resolve-library-id でライブラリIDを解決
  const resolveResult = await client.callTool({
    name: "resolve-library-id",
    arguments: { libraryName },
  });
  console.log("Library resolved:", resolveResult.content);

  // get-library-docs でドキュメントを取得
  const docsResult = await client.callTool({
    name: "get-library-docs",
    arguments: {
      context7CompatibleLibraryID: resolveResult.content[0].text,
      topic,
      tokens: 5000,
    },
  });

  await client.close();
  return docsResult.content[0].text;
}

// 使用例: Honoのミドルウェアドキュメントを取得
const docs = await queryContext7("hono", "middleware bearer auth");
console.log(docs);
```

### 使い方のコツ

- プロンプトに `use context7` を付けるだけで自動的にドキュメント参照が有効になります
- ライブラリ名は正確に指定するほど精度が上がります
- `tokens` パラメータで取得量を制御可能（デフォルト5000トークン）

---

## Tier 1: Playwright MCP — AIにブラウザを操作させる

### なぜTier 1なのか

E2Eテスト作成、UI動作確認、ビジュアルリグレッション検出をAIエージェントに委任できます。Microsoft公式提供で安定性も高いです。

### セットアップ

```bash
# Chromiumブラウザのインストール（初回のみ）
npx playwright install chromium

# 動作確認
npx -y @playwright/mcp@latest --help
```

MCP設定：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

ヘッドモード（ブラウザUIを表示）で起動する場合：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--headed"]
    }
  }
}
```

### Pythonからplaywright MCPを利用するE2Eテスト生成スクリプト

```python
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_browser_test():
    """Playwright MCPを使ったブラウザテスト自動化の例"""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@playwright/mcp@latest"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ページを開く
            await session.call_tool(
                "browser_navigate",
                arguments={"url": "http://localhost:3000"}
            )

            # スクリーンショットを取得
            result = await session.call_tool(
                "browser_screenshot",
                arguments={}
            )
            print("Screenshot captured")

            # 特定の要素をクリック
            await session.call_tool(
                "browser_click",
                arguments={
                    "element": "Login button",
                    "ref": "button[type=submit]"
                }
            )

            # フォームに入力
            await session.call_tool(
                "browser_type",
                arguments={
                    "element": "Email input",
                    "ref": "input[name=email]",
                    "text": "test@example.com"
                }
            )

            print("Browser test completed successfully")

if __name__ == "__main__":
    asyncio.run(run_browser_test())
```

### 活用パターン

| パターン | プロンプト例 |
|----------|-------------|
| E2Eテスト生成 | 「今のページの操作手順をPlaywrightテストコードとして書き出して」 |
| ビジュアルリグレッション | 「変更前後でスクリーンショットを比較して」 |
| フォームバリデーション | 「登録フォームの全エラーパターンを試して」 |
| アクセシビリティ | 「このページのa11y問題を検出して」 |

---

## Tier 1: PostgreSQL MCP — データベースをAIの文脈に接続

### なぜTier 1なのか

スキーマ参照→クエリ生成→実行→結果分析がAIのコンテキスト内で完結します。ターミナルとエディタの往復が劇的に減り、正確なSQL生成が可能になります。

### セットアップ

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://dev:dev@localhost:5432/app_development"
      ]
    }
  }
}
```

### TypeScript + MCP SDKでDBクエリを自動化する実装

以下は、MCPクライアントを使ってPostgreSQLサーバーに接続し、スキーマ取得とクエリ実行を行う例です。

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
}

async function createPostgresClient(databaseUrl: string): Promise<Client> {
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["-y", "@modelcontextprotocol/server-postgres", databaseUrl],
  });

  const client = new Client(
    { name: "db-automation", version: "1.0.0" },
    { capabilities: {} }
  );

  await client.connect(transport);
  return client;
}

async function getSchema(client: Client): Promise<string> {
  // リソース一覧からスキーマ情報を取得
  const resources = await client.listResources();
  const schemaResources = resources.resources.filter(
    (r) => r.uri.startsWith("postgres://")
  );

  const schemas: string[] = [];
  for (const resource of schemaResources) {
    const content = await client.readResource({ uri: resource.uri });
    schemas.push(content.contents[0].text as string);
  }

  return schemas.join("\n");
}

async function executeQuery(client: Client, sql: string): Promise<string> {
  const result = await client.callTool({
    name: "query",
    arguments: { sql },
  });

  return result.content[0].text as string;
}

// 使用例
async function main() {
  const dbUrl = process.env.DATABASE_URL
    || "postgresql://dev:dev@localhost:5432/app_development";

  const client = await createPostgresClient(dbUrl);

  try {
    // スキーマ取得
    const schema = await getSchema(client);
    console.log("=== Database Schema ===");
    console.log(schema);

    // クエリ実行
    const result = await executeQuery(
      client,
      `SELECT date_trunc('day', created_at) as day, COUNT(*)
       FROM users
       WHERE created_at > NOW() - INTERVAL '7 days'
       GROUP BY day
       ORDER BY day DESC`
    );
    console.log("\n=== Query Result ===");
    console.log(result);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
```

### セキュリティのベストプラクティス

```bash
# READ ONLY権限のDBユーザーを作成（PostgreSQL）
psql -U postgres -c "
CREATE ROLE mcp_readonly WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE app_development TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mcp_readonly;
"

# この読み取り専用ユーザーでMCPサーバーを接続
# postgresql://mcp_readonly:secure_password@localhost:5432/app_development
```

---

## Tier 2: Sentry MCP — エラー監視をAIワークフローに統合

### なぜTier 2なのか

Sentryを既に導入しているチームには非常に強力ですが、「Sentryを使っている」ことが前提条件です。導入済みチームにとっては、エラー発見→原因特定→修正のサイクルが劇的に高速化します。

### セットアップ

```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "sntrys_YOUR_TOKEN_HERE",
        "SENTRY_ORG": "your-org-slug"
      }
    }
  }
}
```

Auth Tokenの発行手順：
1. Sentry管理画面 → Settings → Auth Tokens
2. 必要スコープ: `event:read`, `project:read`, `org:read`
3. トークンは `sntrys_` プレフィックスで始まります

### エラートリアージ自動化スクリプト（Shell）

以下は、Sentry APIを直接叩いてエラー一覧を取得し、MCPと組み合わせるためのヘルパースクリプトです。

```bash
#!/bin/bash
# sentry-triage.sh — 未解決エラーの日次トリアージ

SENTRY_ORG="your-org"
SENTRY_PROJECT="your-project"
SENTRY_TOKEN="${SENTRY_AUTH_TOKEN}"

# 直近24時間の未解決エラーを取得
echo "=== Sentry未解決エラー (直近24h) ==="
curl -s \
  -H "Authorization: Bearer ${SENTRY_TOKEN}" \
  "https://sentry.io/api/0/projects/${SENTRY_ORG}/${SENTRY_PROJECT}/issues/?query=is:unresolved+firstSeen:-24h&sort=freq" \
  | jq '.[] | {title: .title, count: .count, firstSeen: .firstSeen, level: .level}'

echo ""
echo "=== エラー件数サマリー ==="
curl -s \
  -H "Authorization: Bearer ${SENTRY_TOKEN}" \
  "https://sentry.io/api/0/projects/${SENTRY_ORG}/${SENTRY_PROJECT}/issues/?query=is:unresolved" \
  | jq 'length' \
  | xargs -I {} echo "未解決エラー合計: {} 件"

# MCPサーバー経由で詳細分析する場合の起動確認
echo ""
echo "=== MCP Server Status ==="
if pgrep -f "@sentry/mcp-server" > /dev/null; then
  echo "Sentry MCP: Running"
else
  echo "Sentry MCP: Not running (Claude Code/Cursorから自動起動されます)"
fi
```

### 実践的なワークフロー

1. **朝のトリアージ**: 「昨日発生した新規エラーを重要度順に一覧表示して」
2. **影響度分析**: 「このエラーの影響ユーザー数と発生頻度を教えて」
3. **根本原因特定**: 「スタックトレースからコードの該当箇所を特定して修正案を出して」
4. **修正→デプロイ確認**: 「修正後にこのエラーが再発していないか確認して」

---

## Tier 2: Firecrawl — WebページをLLMが理解できる形に変換

### なぜTier 2なのか

Webスクレイピングのニーズは普遍的ですが、使用頻度は人によります。ドキュメント参照・競合調査・コンテンツ移行が多い方には必須級です。JavaScript描画後のコンテンツも取得でき、SPA対応力が高い点が強みです。

### セットアップ

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

セルフホスト版（ローカル実行）を使う場合：

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-YOUR_API_KEY",
        "FIRECRAWL_API_URL": "http://localhost:3002"
      }
    }
  }
}
```

### TypeScriptでFirecrawl MCPを活用した競合分析ツール

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { writeFileSync } from "fs";

interface CompetitorPage {
  url: string;
  markdown: string;
  metadata: Record<string, string>;
}

async function scrapeCompetitors(urls: string[]): Promise<CompetitorPage[]> {
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["-y", "firecrawl-mcp"],
    env: {
      FIRECRAWL_API_KEY: process.env.FIRECRAWL_API_KEY || "",
    },
  });

  const client = new Client(
    { name: "competitor-analyzer", version: "1.0.0" },
    { capabilities: {} }
  );

  await client.connect(transport);
  const results: CompetitorPage[] = [];

  for (const url of urls) {
    try {
      const result = await client.callTool({
        name: "firecrawl_scrape",
        arguments: {
          url,
          formats: ["markdown"],
          onlyMainContent: true,
        },
      });

      const content = JSON.parse(result.content[0].text as string);
      results.push({
        url,
        markdown: content.markdown || "",
        metadata: content.metadata || {},
      });

      console.log(`✓ Scraped: ${url}`);
    } catch (error) {
      console.error(`✗ Failed: ${url}`, error);
    }
  }

  await client.close();
  return results;
}

// 使用例: 競合3社のランディングページを比較分析
async function main() {
  const competitors = [
    "https://competitor-a.com/pricing",
    "https://competitor-b.com/pricing",
    "https://competitor-c.com/pricing",
  ];

  const pages = await scrapeCompetitors(competitors);

  // Markdown形式でレポート出力
  const report = pages
    .map((p) => `## ${p.url}\n\n${p.markdown.slice(0, 2000)}`)
    .join("\n\n---\n\n");

  writeFileSync("competitor-analysis.md", report);
  console.log(`\nReport saved: competitor-analysis.md (${pages.length} pages)`);
}

main().catch(console.error);
```

### Firecrawlの主なツール

| ツール名 | 用途 |
|----------|------|
| `firecrawl_scrape` | 単一ページのスクレイピング |
| `firecrawl_crawl` | サイト全体の再帰クロール |
| `firecrawl_map` | サイトマップの取得 |
| `firecrawl_extract` | 構造化データの抽出 |

---

## 全ツール比較テーブル

### 機能マトリクス

| 機能/特性 | Context7 | Playwright MCP | PostgreSQL MCP | Sentry MCP | Firecrawl |
|-----------|----------|----------------|----------------|------------|------------|
| **Tier** | 1（必須） | 1（必須） | 1（必須） | 2（推奨） | 2（推奨） |
| **カテゴリ** | ドキュメント参照 | ブラウザ自動化 | DB操作 | エラー監視 | Webクロール |
| **セットアップ難易度** | ★☆☆ | ★★☆ | ★☆☆ | ★★☆ | ★☆☆ |
| **APIキー必要** | 不要 | 不要 | 不要 | 必要 | 必要 |
| **無料利用** | ○ | ○ | ○ | △（Sentry契約要） | △（無料枠あり） |
| **オフライン利用** | × | ○ | ○ | × | × |
| **セルフホスト** | × | ○ | ○ | × | ○ |
| **Claude Code対応** | ○ | ○ | ○ | ○ | ○ |
| **Cursor対応** | ○ | ○ | ○ | ○ | ○ |
| **VS Code Copilot対応** | ○ | ○ | ○ | ○ | ○ |

### コスト比較

| ツール | 月額コスト | 備考 |
|--------|-----------|------|
| Context7 | 無料 | Upstashインフラ利用 |
| Playwright MCP | 無料 | OSS、ローカル実行 |
| PostgreSQL MCP | 無料 | 自前DB接続 |
| Sentry MCP | $0〜$80+/月 | Sentryプランに依存 |
| Firecrawl | 無料枠500クレジット/月〜 | 従量制 |

---

## ユースケース別おすすめ構成

### 個人開発者（最小構成）

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

**選定理由**: 無料・APIキー不要。最新ドキュメント参照 + ブラウザ動作確認で、個人開発の生産性が大幅に向上します。

### チーム開発（フルスタック構成）

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://mcp_readonly:password@localhost:5432/app_dev"]
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}",
        "SENTRY_ORG": "your-org"
      }
    }
  }
}
```

### セキュリティ制約のある現場（SES等）

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

**選定理由**: APIキー不要でローカル完結。セキュリティポリシーの厳しい環境でも導入しやすい構成です。

---

## MCPサーバーの運用Tips

### プロセス管理とトラブルシューティング

```bash
#!/bin/bash
# mcp-health-check.sh — MCPサーバーのヘルスチェック

echo "=== MCP Server Process Status ==="
ps aux | grep -E "(context7|playwright|server-postgres|sentry.*mcp|firecrawl)" | grep -v grep

echo ""
echo "=== Memory Usage ==="
ps aux | grep -E "(context7|playwright|server-postgres|sentry.*mcp|firecrawl)" \
  | grep -v grep \
  | awk '{printf "%-50s %s MB\n", $11, $6/1024}'

echo ""
echo "=== Direct Server Test ==="
# Context7の動作確認（stdioプロトコルなので起動できればOK）
timeout 5 npx -y @upstash/context7-mcp@latest <<< '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' 2>/dev/null
if [ $? -eq 0 ]; then
  echo "Context7: OK"
else
  echo "Context7: Starting...(initial npm install may take time)"
fi
```

### .gitignoreの設定

```gitignore
# MCP設定ファイル（APIキーを含む可能性があるため）
.cursor/mcp.json
.vscode/mcp.json
.mcp.json

# ただしテンプレートはコミットする
!.cursor/mcp.json.example
!.vscode/mcp.json.example
```

### セキュリティチェックリスト

- [ ] DB接続はREAD ONLYユーザーを使用
- [ ] APIキーは環境変数で管理（ハードコードしない）
- [ ] MCP設定ファイルは`.gitignore`に追加済み
- [ ] Sentry Tokenのスコープは最小限
- [ ] Firecrawlで社内URLをクロールしない
- [ ] 本番DBに直接接続しない

---

## Tier 3: 選択型MCPサーバー

必要に応じて追加を検討するMCPサーバーです。

| MCPサーバー | 用途 | 導入判断基準 |
|-------------|------|-------------|
| GitHub MCP | Issue/PR操作 | GitHub APIを頻繁に使うワークフロー |
| Slack MCP | メッセージ送受信 | Slack連携自動化が必要な場合 |
| Filesystem MCP | ファイル操作 | サンドボックス環境でのファイルアクセス |
| Memory MCP | 永続記憶 | 長期コンテキスト保持が必要なエージェント |
| Brave Search MCP | Web検索 | リアルタイム情報取得 |

---

## MCPエコシステムの今後（2026年後半の展望）

1. **リモートMCPサーバー**: ローカルプロセスからクラウドホスト型への移行が進行中
2. **OAuth 2.0認証標準化**: MCPサーバーの認証フローが統一される方向
3. **IDE統合の深化**: JetBrains IDEでのネイティブサポートが2026年後半に予定
4. **エンタープライズ対応**: SSO連携、監査ログ、RBAC（Role-Based Access Control）機能

---

## まとめ：30分で構築するMCP環境

| ステップ | やること | 所要時間 |
|----------|----------|----------|
| 1 | Claude Code / Cursorを最新版に更新 | 5分 |
| 2 | Context7を設定ファイルに追加 | 2分 |
| 3 | Playwright MCPを追加 + `npx playwright install chromium` | 5分 |
| 4 | PostgreSQL MCP（READ ONLYユーザー作成含む） | 10分 |
| 5 | 動作確認（各MCPサーバーに問いかけ） | 10分 |

MCPの真価は「AIエージェントが文脈を持ってタスクを遂行できること」にあります。ドキュメントを参照し、ブラウザで確認し、DBを操作し、エラーを追跡する——人間のエンジニアと同じワークフローをAIが実行できる環境を、ぜひ今日から構築してみてください。

---

## 参考リンク

- [MCP公式仕様](https://spec.modelcontextprotocol.io/)
- [MCP SDK (TypeScript)](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP SDK (Python)](https://github.com/modelcontextprotocol/python-sdk)
- [Context7](https://github.com/upstash/context7)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [PostgreSQL MCP Server](https://github.com/modelcontextprotocol/servers)

---

**合同会社Radineer**では、MCPサーバーを活用したAIエージェント経営システムを構築・運用しています。
https://radineer.asia

---

## 💼 フリーランスエンジニアの案件をお探しですか？

**SES解体新書 フリーランスDB**では、高単価案件を多数掲載中です。

- ✅ マージン率公開で透明な取引
- ✅ AI/クラウド/Web系の厳選案件
- ✅ 専任コーディネーターが単価交渉をサポート

▶ **[無料でエンジニア登録する](https://radineer.asia/freelance/register?utm_source=qiita&utm_medium=article&utm_campaign=2026%E5%B9%B4%E6%9C%80%E6%96%B0-mcp%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC5%E9%81%B8%E3%81%AE%E5%B0%8E%E5%85%A5%E3%83%BB%E5%AE%9F%E8%A3%85%E3%82%AC%E3%82%A4%E3%83%89-%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97%E3%81%8B%E3%82%89typescript-python%E9%80%A3%E6%90%BA%E3%81%BE%E3%81%A7%E5%BE%B9%E5%BA%95%E8%A7%A3%E8%AA%AC)**
