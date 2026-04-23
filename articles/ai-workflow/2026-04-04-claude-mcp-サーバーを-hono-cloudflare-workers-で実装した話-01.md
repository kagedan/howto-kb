---
id: "2026-04-04-claude-mcp-サーバーを-hono-cloudflare-workers-で実装した話-01"
title: "Claude MCP サーバーを Hono + Cloudflare Workers で実装した話"
url: "https://zenn.dev/scrpgil/articles/a770cb68a63826"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "GPT", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

## はじめに

私は個人プロジェクトとして、週次カンバンボード「LetWeek」を開発している。ポモドーロ、GTD、すきま時間予定表——これらのテクニックを一箇所で実践できるツールが欲しくて作り始めたものだ。

開発を進める中で、ひとつの設計判断をした。**アプリ内にAIチャットを持たない**ということだ。

私自身がすでにChatGPTやClaudeを日常的に使っていたので、LetWeekのデータにそれらのAIからアクセスできるようにした方が自然だろうと考えた。そこで [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) を使ってClaude連携を実装した。stdioとStreamable HTTPの両方を作ったが、この記事ではCloudflare Workers上で動く **Streamable HTTP版** について書く。

## 全体のアーキテクチャ

```
Claude Desktop / claude.ai
    │
    │  POST /mcp  (Streamable HTTP)
    │  Authorization: Bearer <token>
    ▼
Cloudflare Workers (Hono)
    │
    ├── OAuth 2.1 PKCE 認証
    ├── MCP サーバー (per-request, stateless)
    │     ├── 15 Tools
    │     └── 4 Prompts
    └── D1 (SQLite) via Drizzle ORM
```

Workersはリクエストごとにステートレスなので、MCPサーバーも毎回新しく生成する。認証はClaude Desktopのようなpublic client向けにOAuth 2.1 PKCEを用意した。

## MCPエンドポイントの実装

核となるコードはこれだけだ。

```
app.post('/', async (c) => {
  const userId = await authenticateRequest(c);
  if (!userId) return c.json({ error: 'Unauthorized' }, 401);

  const server = createMcpServer(c.get('db'), userId);

  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined, // stateless mode
  });
  await server.connect(transport);

  const response = await transport.handleRequest(c.req.raw);
  return response ?? c.json({ error: 'No response' }, 400);
});
```

`@modelcontextprotocol/sdk` の `WebStandardStreamableHTTPServerTransport` がWeb Standard APIの `Request` / `Response` を使うので、Cloudflare Workersとそのまま互換する。プロトコル処理はSDKが全部やってくれるので、自分が書くのはToolsとPromptsのビジネスロジックだけだ。

## 何を実装したか

**Tools (15個)**: タスクのCRUD、ゴール設定・更新、統計取得、プロフィール更新、カレンダーイベント取得など。ボード上でできる操作はほぼすべてClaude経由でも実行できるようにした。

**Prompts (4個)**:

| Prompt | 用途 |
| --- | --- |
| `daily_brief` | 朝。今日のタスク + ゴール進捗 |
| `daily_review` | 夜。日のサマリー + 振り返り |
| `weekly_goal_setting` | 週の始め。先週振り返り + ゴール設定 |
| `weekly_review` | 週末。統計 + リフレクション |

各プロンプトには行動原則（「事実と選択肢を提示する」「個人的な共有にはNoted.と受け止めて次のステップを返す」等）を埋め込んでいる。AIの応答を直接制御するのではなく、コンテキストと原則を渡して間接的にガイドする設計だ。

**OAuth 2.1 PKCE**: `/.well-known/oauth-authorization-server` のメタデータ発見、Dynamic Client Registration、認可コード発行、トークン交換、リフレッシュ、失効。エンドポイントは7つ。PKCEのSHA-256検証にはWorkersの `crypto.subtle` がそのまま使えたので、外部ライブラリは不要だった。

## 使ってみてどうか

自分自身がユーザーとして使ってみて、朝起きてClaudeに「今日のブリーフィング」と言うだけで、1週間の文脈を踏まえた提案が返ってくるのはとても楽。

## まとめ

* Hono + Cloudflare Workers + `@modelcontextprotocol/sdk` でMCPサーバーを実装できる
* Stateless per-requestモデルがWorkersと相性が良い
* OAuth 2.1 PKCEはWeb Crypto APIだけで実装可能
* MCPは「AIにツールを公開する」という発想で、REST API設計の延長線上にある
* なお、実装の大部分はClaude Codeで書いた
