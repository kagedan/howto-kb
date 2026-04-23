---
id: "2026-04-20-mastra-で作る-aiエージェント26-mastra-platform-のdbをneonpost-01"
title: "Mastra で作る AIエージェント(26) Mastra Platform のDBをNeon（PostgreSQL）に切り替える"
url: "https://zenn.dev/shiromizuj/articles/3ed824b8d97648"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

[Mastra で作る AI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第26回です。

---

[前回](https://zenn.dev/shiromizuj/articles/9ccd85865dca81)は、Mastra Platform にプロジェクトをデプロイするところまで試しました。エージェントも動き、Studio も使えるようになり、一通りのことはできています。

しかしここで一つ問題があります。今の構成では、各種ストレージに **LibSQL（SQLite）と DuckDB のローカルファイル**を使っています。これはローカル開発には便利なのですが、本番環境で使い続けると以下の 2 つの問題が生じます。

* **デプロイするたびにデータが初期化される** — Mastra Platform はエフェメラルなファイルシステムを使用しているため、デプロイのたびにローカルファイルが消えてしまいます。会話履歴も RAG データも、一切が白紙に戻ります。
* **同時アクセスに弱い** — SQLite はファイルロックで排他制御するため、複数ユーザーが同時にアクセスすると競合が起きやすく、本番負荷には向きません。

「DB の永続化」はある意味、Mastra Platform の問題というより**本番デプロイ全般に共通する問題**です。今回はその解決策として、各種 DB を外部の永続 DB サービスに切り替える手順をご紹介します。外部 DB サービスはいろいろあるのですが、今回は **Neon（サーバーレス PostgreSQL）** を採用します。

### 外部 PostgreSQL サービスの選択肢

PostgreSQL 互換の外部サービスとしては、たとえば以下のような選択肢があります。

| サービス | 特徴 |
| --- | --- |
| **Neon** | サーバーレス PostgreSQL。コンピュートとストレージを分離した設計で、未使用時はコンピュートが自動停止。pgvector を標準サポート。無料枠あり。 |
| **Supabase** | PostgreSQL をベースにしたバックエンドプラットフォーム。認証・ストレージ・リアルタイム機能なども含む。フルスタックに便利だが、DB だけ使いたい場合は機能過多になりやすい。 |
| **PlanetScale** | MySQL 互換のサーバーレス DB。PostgreSQL ではないため `@mastra/pg` はそのまま使えない。 |
| **Render / Railway の Postgres** | VPS 系のマネージド PostgreSQL。常時起動型でシンプルだが、無料枠は限定的。 |
| **RDS (AWS) / Cloud SQL (GCP)** | クラウド大手のマネージド PostgreSQL。本格的な本番環境向けだが、設定の手間とコストが大きい。 |

今回 **Neon を採用した理由**は主に 3 つです。

1. **pgvector を標準サポートしている** — RAG のベクトルストア（`PgVector`）の移行先として、一つの DB で ストレージと ベクトルデータの両方を賄えます
2. **`@mastra/pg` が Neon と相性よく動く** — Mastra の公式パッケージが PostgreSQL を前提に設計されており、Neon の接続文字列をそのまま渡すだけで動作します
3. **無料枠で試しやすい** — 今回のような実験・小規模本番には無料プランで十分です。コンピュートが自動停止するためコストも抑えられます

## BEFORE: libsql・DuckDB を使っている

まず、切り替え前の状態を整理しておきましょう。各種ストレージの役割分担はこうなっています。

| 役割 | 変更前 |
| --- | --- |
| 会話履歴・ワークフロー・メトリクス | `LibSQLStore`（`file:./mastra.db`） |
| Observability（Logs・Traces） | `ObservabilityStorageDuckDB`（`mastra.duckdb`） |
| RAG ベクトルデータ | `LibSQLVector`（`file:./rag-data/mastra-vectors.db`） |

### `src/mastra/index.ts`（変更前）

```
import { Mastra } from '@mastra/core/mastra';
import { SimpleAuth } from '@mastra/core/server';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import { DuckDBConnection, ObservabilityStorageDuckDB } from '@mastra/duckdb';
import { MastraCompositeStore } from '@mastra/core/storage';
import { Observability, DefaultExporter, CloudExporter, SensitiveDataFilter } from '@mastra/observability';
import { weatherWorkflow } from './workflows/weather-workflow';
import { weatherAgent } from './agents/weather-agent';
import { ragAgent } from './agents/rag-agent';
import { ragVector } from './vectors/rag-vector';
// ...（スコアラーの import 省略）

export const mastra = new Mastra({
  server: {
    auth: new SimpleAuth({
      tokens: {
        [process.env.API_TOKEN!]: { id: 'user-1', name: 'Admin', role: 'admin' },
      },
    }),
  },
  workflows: { weatherWorkflow },
  agents: { weatherAgent, ragAgent },
  vectors: { ragVector },
  // ...（スコアラー省略）
  storage: new MastraCompositeStore({
    id: 'composite-storage',
    default: new LibSQLStore({
      id: 'mastra-storage',
      url: 'file:./mastra.db',  // ← ローカルファイル
    }),
    domains: {
      observability: new ObservabilityStorageDuckDB({
        db: new DuckDBConnection({ path: 'mastra.duckdb' }),  // ← ローカルファイル
      }),
    },
  }),
  logger: new PinoLogger({ name: 'Mastra', level: 'info' }),
  observability: new Observability({ /* ... */ }),
});
```

会話履歴は `LibSQLStore`（`mastra.db`）に、Observability（Logs・Traces）は `ObservabilityStorageDuckDB`（`mastra.duckdb`）に分けて管理しているため、`MastraCompositeStore` で 2 つを束ねています。

### `src/mastra/vectors/rag-vector.ts`（変更前）

```
import { LibSQLVector } from '@mastra/libsql';
import * as fs from 'fs';
import * as path from 'path';

const VECTOR_DB_URL = process.env.VECTOR_DB_URL
  ?? `file:${path.join(process.cwd(), 'rag-data', 'mastra-vectors.db')}`;

if (VECTOR_DB_URL.startsWith('file:')) {
  const filePath = VECTOR_DB_URL.replace(/^file:/, '');
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

export const ragVector = new LibSQLVector({
  id: 'rag-vector',
  url: VECTOR_DB_URL,
  authToken: process.env.VECTOR_DB_AUTH_TOKEN,
});

export const RAG_INDEX_NAME = 'rag_index';
export const EMBEDDING_DIMENSION = 1536;
```

ローカル開発時はファイルパスを自動組み立てし、Platform デプロイ時は `VECTOR_DB_URL` 環境変数で LibSQL 互換の外部サービス（Turso など）に切り替える設計でした。

### BEFORE の状態を Platform で動かすと…

エージェントの呼び出しも Studio での操作も一見正常に動いています。

![](https://static.zenn.studio/user-upload/02dae497d3bb-20260413.png)  
*エージェント呼び出しは正常に動く*

メトリクス（スコアラー結果）も記録されています。

![](https://static.zenn.studio/user-upload/8b8c419f479c-20260413.png)  
*スコアラー一覧*

![](https://static.zenn.studio/user-upload/d93254867c36-20260413.png)  
*スコアラー詳細*

Traces と Logs もきちんと記録されています。

![](https://static.zenn.studio/user-upload/db4b46026670-20260413.png)  
*Traces*

![](https://static.zenn.studio/user-upload/cd21992fe5b6-20260413.png)  
*Logs*

これだけ見ると「問題なく動いている」ように見えてしまいますが、**再デプロイすると全てのデータが消えます**。libsql・DuckDB が書き込んでいるのはコンテナ内のローカルファイルであり、デプロイのたびに新しいコンテナが起動してデータは消滅します。本番運用では完全に使い物になりません。

---

## AFTER: Neon（PostgreSQL）に切り替える

切り替え後の構成はこうなります。

| 役割 | 変更後 |
| --- | --- |
| 会話履歴・ワークフロー | `PostgresStore`（Neon） |
| Observability（Logs・Traces） | `PostgresStore`（Neon・同一DB） |
| RAG ベクトルデータ | `PgVector`（Neon with pgvector） |

`@mastra/pg` の `PostgresStore` はストレージと Observability の両方を 1 つで担えるため、`MastraCompositeStore` が不要になります。`PostgresStore` と `PgVector` は同じ Neon DB 内の別テーブルを使用するため、接続文字列を共有しても問題ありません。

> **Metrics（スコアラー結果）について**: 現時点で Mastra の `PostgresStore` は Metrics（スコアラー結果）の永続化に対応していません。そのため、今回の移行対象には含めていません。Platform 上でも Metrics を永続化したい場合は、ClickHouse を別途用意して `MastraCompositeStore` でストレージと組み合わせる構成が必要です。今回のブログ記事では「Metrics なし・そのほかは永続化」で割り切っています。

---

## Step 1. Neon のセットアップ

### アカウント作成

まず [Neon の公式サイト](https://neon.com/) にアクセスし、「Sign Up」からアカウントを作成します。GitHub アカウントで登録するのが一番スムーズです。

![](https://static.zenn.studio/user-upload/2c5b130cd0b4-20260413.png)  
*サインアップ画面。GitHub、Google、メールアドレスのいずれかで登録できます*

GitHub 認証を選択します。

![](https://static.zenn.studio/user-upload/648940cb9f7b-20260413.png)

認証が完了すると、Neon の管理画面に入ります。

![](https://static.zenn.studio/user-upload/5fc89098269f-20260413.png)

![](https://static.zenn.studio/user-upload/037a630e2323-20260413.png)

### プロジェクト作成

プロジェクト名とリージョンを設定します。 レイテンシを抑えるために **AWS Tokyo (ap-northeast-1)** を選びたいところですが、選択肢にないので **シンガポール** を選びます。

![](https://static.zenn.studio/user-upload/3a5e6b705417-20260413.png)  
*プロジェクト名とリージョンを設定する*

「Create Project」をクリックするとわずか数秒で DB が立ち上がります。これがサーバーレス PostgreSQL の強みです。

### 接続文字列のコピー

プロジェクト作成後に表示される **Connection string** をコピーしておきます。この文字列が設定の核になります。

![](https://static.zenn.studio/user-upload/c847be7778ec-20260413.png)

```
postgresql://username:password@ep-xxx-xxx.ap-northeast-1.aws.neon.tech/dbname?sslmode=require
```

Neon ダッシュボードはこのような見た目です。SQL エディタも内蔵されており、ブラウザから直接 SQL を実行できます。

![](https://static.zenn.studio/user-upload/66252710fa86-20260413.png)

### 接続確認

SQL エディタで `SELECT 1;` を実行して接続を確認します。

![](https://static.zenn.studio/user-upload/235fae0bfc62-20260413.png)

### pgvector 拡張の有効化

RAG のベクトルストアに使うため、pgvector 拡張を有効化します。Neon は標準でサポートしていますが、念のため SQL コンソールで実行しておきましょう。

```
CREATE EXTENSION IF NOT EXISTS vector;
```

![](https://static.zenn.studio/user-upload/e0b907a4c070-20260413.png)

> **テーブルの手動作成は不要です。** `PostgresStore` はサーバー起動時に、`PgVector` は `createIndex()` 呼び出し時に、それぞれ必要なテーブルを自動生成します。

---

## Step 2. パッケージのインストール

不要になった LibSQL・DuckDB パッケージは後で削除できます（他で参照していないことを確認してから）。

```
pnpm remove @mastra/libsql @mastra/duckdb
```

---

## Step 3. 環境変数の設定

### ローカル（`.env`）

`.env` に `DATABASE_URL` を追加します。`VECTOR_DB_URL` / `VECTOR_DB_AUTH_TOKEN` は不要になります。

```
# Neon 接続文字列（ストレージ・Observability・ベクトルストアで共有）
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.ap-northeast-1.aws.neon.tech/dbname?sslmode=require

# 以下は削除 or コメントアウト
# VECTOR_DB_URL=...
# VECTOR_DB_AUTH_TOKEN=...
```

### Mastra Platform ダッシュボード

Platform 側の環境変数も更新が必要です。`DATABASE_URL` を追加し、`VECTOR_DB_URL` / `VECTOR_DB_AUTH_TOKEN` が設定済みの場合は削除します。

1. [projects.mastra.ai](https://projects.mastra.ai/) を開く
2. プロジェクト → **Server → Environment Variables**
3. `DATABASE_URL` に Neon の接続文字列を設定

![](https://static.zenn.studio/user-upload/6e578a1ab1ca-20260413.png)  
*Platform の Environment Variables 画面で DATABASE\_URL を設定する*

---

## Step 4. `src/mastra/index.ts` の修正

`MastraCompositeStore` を廃止し、`PostgresStore` 一本に集約します。`DATABASE_URL` が設定されていれば Neon を、なければ LibSQL にフォールバックする形にすることで、ローカル開発時は今まで通り動かせます。

```
  import { Mastra } from '@mastra/core/mastra';
  import { SimpleAuth } from '@mastra/core/server';
  import { PinoLogger } from '@mastra/loggers';
- import { LibSQLStore } from '@mastra/libsql';
- import { DuckDBConnection, ObservabilityStorageDuckDB } from '@mastra/duckdb';
- import { MastraCompositeStore } from '@mastra/core/storage';
+ import { PostgresStore } from '@mastra/pg';
+ import { LibSQLStore } from '@mastra/libsql';
  import { Observability, DefaultExporter, CloudExporter, SensitiveDataFilter } from '@mastra/observability';
  // ...（他の import は変更なし）

  export const mastra = new Mastra({
    // ...（server, workflows, agents, vectors, scorers は変更なし）
-   storage: new MastraCompositeStore({
-     id: 'composite-storage',
-     default: new LibSQLStore({
-       id: 'mastra-storage',
-       url: 'file:./mastra.db',
-     }),
-     domains: {
-       observability: new ObservabilityStorageDuckDB({
-         db: new DuckDBConnection({ path: 'mastra.duckdb' }),
-       }),
-     },
-   }),
+   storage: process.env.DATABASE_URL
+     ? new PostgresStore({
+         id: 'mastra-storage',
+         connectionString: process.env.DATABASE_URL,
+         ssl: { rejectUnauthorized: false },
+       })
+     : new LibSQLStore({ id: 'mastra-storage', url: 'file:./mastra.db' }),
    logger: new PinoLogger({ name: 'Mastra', level: 'info' }),
    observability: new Observability({ /* ... */ }),
  });
```

`PostgresStore` は Observability（Logs・Traces）も自動的に担うため、`ObservabilityStorageDuckDB` と `MastraCompositeStore` は不要になります。

---

## Step 5. `src/mastra/vectors/rag-vector.ts` の修正

`LibSQLVector` を `PgVector` に差し替えます。`DATABASE_URL` がある場合は Neon を、ない場合は LibSQL にフォールバックします。`RAG_INDEX_NAME` と `EMBEDDING_DIMENSION` の定数はそのままです。

```
- import { LibSQLVector } from '@mastra/libsql';
- import * as fs from 'fs';
- import * as path from 'path';
+ import { PgVector } from '@mastra/pg';
+ import { LibSQLVector } from '@mastra/libsql';

- const VECTOR_DB_URL = process.env.VECTOR_DB_URL
-   ?? `file:${path.join(process.cwd(), 'rag-data', 'mastra-vectors.db')}`;
-
- if (VECTOR_DB_URL.startsWith('file:')) {
-   const filePath = VECTOR_DB_URL.replace(/^file:/, '');
-   fs.mkdirSync(path.dirname(filePath), { recursive: true });
- }
-
- export const ragVector = new LibSQLVector({
-   id: 'rag-vector',
-   url: VECTOR_DB_URL,
-   authToken: process.env.VECTOR_DB_AUTH_TOKEN,
- });
+ export const ragVector = process.env.DATABASE_URL
+   ? new PgVector({
+       id: 'rag-vector',
+       connectionString: process.env.DATABASE_URL,
+       ssl: { rejectUnauthorized: false },
+     })
+   : new LibSQLVector({ id: 'rag-vector', url: 'file:./rag-data/mastra-vectors.db' });

  export const RAG_INDEX_NAME = 'rag_index';
  export const EMBEDDING_DIMENSION = 1536;
```

---

## Step 6. RAG データの再 ingest

ベクトルストアが新しい Neon DB に変わったため、既存の埋め込みデータを再投入する必要があります。

---

## Step 7. ビルド確認と Platform への再デプロイ

ローカルでビルドエラーがないことを確認したら、Platform へデプロイします。

```
npm run build
mastra server deploy
```

Platform ダッシュボードで `DATABASE_URL` が設定済みであることを確認してからデプロイしてください。

---

## 切り替え後の動作確認

再デプロイ後、エージェントを呼び出してみます。

![](https://static.zenn.studio/user-upload/7da6a832559f-20260413.png)  
*エージェントが正常に動いています*

Metrics 画面を確認します。スコアラーの結果がきちんと記録されています。

![](https://static.zenn.studio/user-upload/ca2e355d9113-20260413.png)  
*Metrics（スコアラー結果）*

Traces も正常に記録されています。

![](https://static.zenn.studio/user-upload/93fff493f871-20260413.png)  
*Traces*

Logs も問題なく記録されています。

![](https://static.zenn.studio/user-upload/5cb8d1f1eb9e-20260413.png)  
*Logs*

今度は**再デプロイしてもデータが消えません**。Neon の DB にデータが永続化されているからです。

---

## まとめ

今回の変更のポイントをまとめます。

1. **`MastraCompositeStore` を廃止** — `PostgresStore` がストレージと Observability の両方を担えるため、2 つの DB で管理する必要がなくなります
2. **接続文字列の共有** — `PostgresStore` と `PgVector` は同じ Neon DB 内の別テーブルを使うため、`DATABASE_URL` 1 つで管理できます
3. **テーブルの自動生成** — `PostgresStore` は起動時に、`PgVector` は `createIndex()` 時に必要なテーブルを自動作成するため、マイグレーション作業は不要です
4. **フォールバック設計** — `DATABASE_URL` がなければ LibSQL にフォールバックするようにしておくと、ローカル開発環境への影響を最小限に抑えられます
5. **RAG データの再 ingest が必要** — ベクトルストアが変わるため、移行後は必ず `npm run ingest` を実行してください

本番環境では今回のように外部の永続 DB を使うことが前提です。Neon は無料プランでも十分使えるため、まずは試してみてください。

次回は Mastra Platform でWorkspaces機能を使ってみます。

[>> 次回 : (27) Mastra Platform で Workspace 機能を動かす](https://zenn.dev/shiromizuj/articles/b7692eb3e87c80)
