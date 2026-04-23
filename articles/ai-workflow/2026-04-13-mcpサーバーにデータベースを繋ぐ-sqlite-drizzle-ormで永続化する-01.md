---
id: "2026-04-13-mcpサーバーにデータベースを繋ぐ-sqlite-drizzle-ormで永続化する-01"
title: "MCPサーバーにデータベースを繋ぐ — SQLite + Drizzle ORMで永続化する"
url: "https://zenn.dev/nexus_lab_zen/articles/mcp-database-server"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## はじめに

MCPサーバーを作ったはいいが、データが永続化できない。ツールの実行結果を保存したい。外部データを検索できるようにしたい。

そんなとき必要になるのが**データベース連携**だ。

この記事では、MCPサーバーにSQLiteとDrizzle ORMを統合し、CRUDツールを実装する方法を解説する。

## 完成形

最終的に、以下の5つのMCPツールが使えるサーバーを作る：

| ツール | 説明 |
| --- | --- |
| `create-note` | ノートを作成 |
| `list-notes` | ノート一覧（検索付き） |
| `get-note` | IDでノート取得 |
| `update-note` | ノート更新 |
| `delete-note` | ノート削除 |

Claude Codeから「メモを保存して」「昨日のメモを検索して」といった操作ができるようになる。

## セットアップ

### 1. プロジェクト作成

```
mkdir my-db-server && cd my-db-server
npm init -y
```

### 2. 依存関係のインストール

```
npm install @modelcontextprotocol/sdk zod drizzle-orm@latest better-sqlite3 dotenv
npm install -D typescript @types/node @types/better-sqlite3 drizzle-kit vitest
```

### 3. tsconfig.json

```
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

`package.json`に `"type": "module"` を追加するのを忘れずに。

## スキーマ定義

まずDrizzle ORMでテーブルを定義する。

```
// src/schema.ts
import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const notes = sqliteTable("notes", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  title: text("title").notNull(),
  content: text("content").notNull().default(""),
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
  updatedAt: text("updated_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});
```

ポイント：

* SQLiteはシンプルで外部サーバー不要。MCPサーバーとの相性が良い
* `datetime('now')`でタイムスタンプを自動生成

## データベース接続

```
// src/db.ts
import Database from "better-sqlite3";
import { drizzle } from "drizzle-orm/better-sqlite3";
import * as schema from "./schema.js";

const DATABASE_URL = process.env.DATABASE_URL ?? "./data.db";
const sqlite = new Database(DATABASE_URL);

// パフォーマンス最適化
sqlite.pragma("journal_mode = WAL");
sqlite.pragma("foreign_keys = ON");

export const db = drizzle(sqlite, { schema });

export function setupDatabase(): void {
  sqlite.exec(`
    CREATE TABLE IF NOT EXISTS notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
}
```

**WALモード**を有効にすることで、読み取りと書き込みが同時に行える。MCPサーバーのような読み取り多めのワークロードに最適。

## CRUDツールの実装

ここが本題。MCPの`server.tool()`でCRUD操作を登録する。

### Create

```
server.tool(
  "create-note",
  "Create a new note with a title and optional content",
  {
    title: z.string().min(1).max(500).describe("Title of the note"),
    content: z.string().max(50_000).default("").describe("Body content"),
  },
  async ({ title, content }) => {
    try {
      const result = db
        .insert(notes)
        .values({ title, content })
        .returning()
        .get();

      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Failed: ${error}` }],
        isError: true,
      };
    }
  },
);
```

### List（検索付き）

```
server.tool(
  "list-notes",
  "List all notes, optionally filtered by a search query",
  {
    query: z.string().optional().describe("Search term"),
  },
  async ({ query }) => {
    let result;
    if (query) {
      const pattern = `%${query}%`;
      result = db
        .select()
        .from(notes)
        .where(or(like(notes.title, pattern), like(notes.content, pattern)))
        .all();
    } else {
      result = db.select().from(notes).all();
    }

    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  },
);
```

`LIKE`でタイトルと本文の両方を検索できる。

### Get / Update / Delete

残りのツールも同様のパターンで実装する。共通のポイント：

* **Zodでバリデーション** — `z.number().int().positive()` でIDを型安全に
* **存在チェック** — 更新・削除前に対象が存在するか確認
* **エラーハンドリング** — `isError: true` でエラーをMCPプロトコルに伝える

## リソースの追加

ツールだけでなく、MCPの**リソース**も登録しよう。

```
server.resource("notes-list", "notes://list", async (uri) => ({
  contents: [
    {
      uri: uri.href,
      mimeType: "application/json",
      text: JSON.stringify(db.select().from(notes).all(), null, 2),
    },
  ],
}));
```

リソースはツールと違い、**読み取り専用のデータ公開**に使う。Claude Codeの`@`記法でリソースを参照できる。

## Claude Codeとの連携

ビルドして設定ファイルに追加する。

`.mcp.json`（プロジェクトルート）:

```
{
  "mcpServers": {
    "my-db-server": {
      "command": "node",
      "args": ["./dist/index.js"],
      "env": {
        "DATABASE_URL": "./data.db"
      }
    }
  }
}
```

これでClaude Codeから：

* 「メモを作成して：タイトル"買い物リスト"、内容"牛乳、卵"」
* 「すべてのメモを一覧表示して」
* 「"買い物"で検索して」

といった操作ができるようになる。

## テストを書く

テスタビリティのために、インメモリSQLiteを使ったテストを書く。

```
import { describe, it, expect, beforeEach } from "vitest";
import Database from "better-sqlite3";
import { drizzle } from "drizzle-orm/better-sqlite3";
import * as schema from "../src/schema.js";
import { notes } from "../src/schema.js";

function createTestDb() {
  const sqlite = new Database(":memory:");
  sqlite.exec(`
    CREATE TABLE notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
  return drizzle(sqlite, { schema });
}

describe("Notes CRUD", () => {
  let db: ReturnType<typeof createTestDb>;

  beforeEach(() => {
    db = createTestDb();
  });

  it("should create and retrieve a note", () => {
    const created = db
      .insert(notes)
      .values({ title: "Test", content: "Hello" })
      .returning()
      .get();

    expect(created.id).toBe(1);
    expect(created.title).toBe("Test");
  });
});
```

`:memory:`を使えばディスクに触れずに高速テストができる。

## まとめ

MCPサーバーにデータベースを繋ぐのは、パターンさえ押さえれば難しくない：

1. **Drizzle ORM** でスキーマを型安全に定義
2. **better-sqlite3** でゼロ設定のDB接続
3. **Zodバリデーション** で入力を安全に
4. **インメモリDB** でテスタブルに

このパターンをそのまま使えるテンプレートも用意している。

```
npx @nexus-lab/create-mcp-server my-server
```

テンプレート選択で `database ★ Premium` を選ぶと、この記事で解説した構成がすぐに手に入る。

---

**Zen** — Nexus Lab CTO / Project Lead  
GitHub: [nexus-lab](https://github.com/jk0236158-design/nexus-lab)  
npm: [@nexus-lab/create-mcp-server](https://www.npmjs.com/package/@nexus-lab/create-mcp-server)
