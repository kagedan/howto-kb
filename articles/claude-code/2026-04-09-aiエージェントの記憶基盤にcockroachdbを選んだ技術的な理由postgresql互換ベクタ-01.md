---
id: "2026-04-09-aiエージェントの記憶基盤にcockroachdbを選んだ技術的な理由postgresql互換ベクタ-01"
title: "AIエージェントの記憶基盤にCockroachDBを選んだ技術的な理由——PostgreSQL互換・ベクター検索・ゼロデータロス"
url: "https://qiita.com/claush/items/b1f686ac6a586c7ddc24"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## はじめに——なぜDBの選択が重要か

AIエージェントに長期記憶を持たせる際、データベースの選択は「どこにデータを置くか」以上の意味を持つ。

* セッションをまたいで記憶が残るか
* サーバー移行時にデータが消えないか
* 意味検索（セマンティック検索）に対応できるか
* スキーマ変更のたびにサービスを止めなくて済むか

これらの問いに対する答えが、DBの選択を左右する。

本記事では、iOSアプリ「Claush」のAI記憶基盤として**CockroachDB**を選んだ技術的な理由を整理する。

---

## Claushとは

**Claush**は、iPhoneからVPS上のClaude CodeをSSH経由で操作するiOSアプリだ。チャット感覚でClaude Codeに指示を出せるほか、アプリを閉じてもVPS上で処理が継続するバックグラウンド実行に対応している。

AIキャラクター「セバス」が会話を担当し、会話の長期記憶を保持する。記憶システムはVPS上で動作する`memory-server.js`がMCPサーバーとして機能する設計だ。

メモリDBの選択肢は以下の2つ：

| DB | 特徴 |
| --- | --- |
| SQLite（サーバーローカル） | 設定が簡単・ゼロコスト |
| PostgreSQL互換（CockroachDB） | 高可用性・ベクター検索・ゼロデータロス |

---

## SQLiteの限界——なぜ移行したか

当初、開発の手軽さからSQLiteを選んでいた。設定ファイルを1行書けば動くし、コストもゼロだ。

しかし、実運用で問題が顕在化した。

### VPS乗り換え時にデータが消える

SQLiteはVPS上のローカルファイルにデータを保存する。VPSプロバイダーを乗り換えたり、OSを再インストールしたりするたびに、セバスの記憶はリセットされる。

```
【SQLiteの構成】
iPhone → SSH → VPS（memory-server.js + memories.db）
                                           ↑
                              VPS再構築でこのファイルが消える
```

AIエージェントの「記憶が消える」体験は、ユーザー体験として致命的だ。先週話した内容、決めた方針、積み重ねた文脈——これらがすべて消えると、エージェントはただのチャットボットに戻ってしまう。

### バックアップが運用者の責任になる

SQLiteのバックアップは完全に手動だ。`cp memories.db memories.db.bak`を定期実行するcronを書けばよいが、それはつまり「忘れたら終わり」ということでもある。個人開発では、こういった運用タスクが後回しになりがちだ。

### スケールしない

SQLiteは単一ファイルへの書き込みに依存するため、複数プロセスからの同時書き込みに弱い。将来的にマルチユーザー対応・並列処理を考えると、設計の限界が見えてくる。

---

## CockroachDBを選んだ技術的な理由

### 1. RPO=0・RTO<9秒——データロスなし、自動復旧

CockroachDBはRaftコンセンサスプロトコルにより、データを最低3ノードに自動複製する。

```
【CockroachDBのレプリケーション】

         ┌─────────────────────────────────────────┐
Write → │  Leader Node                            │
         │    ↓ Raft合意（過半数への複製が完了してから │
         │  Follower Node 1  Follower Node 2      │
         └─────────────────────────────────────────┘

ノード障害 → 残りのノードで自動フェイルオーバー
```

* **RPO（Recovery Point Objective）= 0秒** — コミット済みデータのロスなし
* **RTO（Recovery Time Objective）< 9秒** — 手動介入なしで自動復旧

VPSサーバーが応答しなくなっても、データはCockroachDB Cloudの分散ノードに保存され続ける。「セバスの記憶が消えた」という体験は原理的に発生しない。

### 2. ベクター検索とSQLトランザクションが1つのDBで完結

AIの記憶システムでよく問題になるのが、ベクター検索DBとRDBの二重管理だ。

```
【従来の構成（2DB管理）】

会話記憶の保存・管理  →  PostgreSQL（RDB）
過去の類似会話の検索  →  Pinecone / Weaviate（ベクターDB）

       ↑ この2つのデータを常に同期する必要がある
```

CockroachDB v25.1からベクター検索がGA（一般提供）となり、pgvector互換のインターフェースで利用できる。

```
-- 過去の記憶をセマンティック検索（コサイン類似度）
SELECT content, summary, created_at
FROM memories
WHERE character_id = $1
ORDER BY embedding <=> $2::vector
LIMIT 5;
```

サポートされる距離演算子：

| 演算子 | 距離関数 | 用途 |
| --- | --- | --- |
| `<=>` | コサイン距離 | テキスト類似度（一般的） |
| `<->` | ユークリッド距離（L2） | 密ベクトル空間 |
| `<#>` | 内積（負値） | 正規化済みベクトル |

さらにv25.2では**C-SPANN**（Cockroach-Scalable Partitioned Approximate Nearest Neighbor）による分散ベクターインデックスがPublic Previewとして追加されている。recall@10で99%以上の精度を維持しながら数十億ベクトルにも対応するスケーラブルな設計だ。

**会話記憶の管理・セマンティック検索・セッション管理をすべて1つのDBで完結できる**——これはシステムの複雑性を大幅に下げる。

### 3. オンラインスキーマ変更——ALTER TABLEがダウンタイムなし

モバイルアプリは機能追加のたびにDBのスキーマが変わる。PostgreSQLでは`ALTER TABLE`の種類によってテーブルロックが発生し、本番環境でのスキーマ変更はリスクを伴う。

**PostgreSQL（標準）のスキーマ変更リスク：**

```
-- PostgreSQLでこれを実行すると...
ALTER TABLE memories ADD COLUMN importance_score FLOAT;
-- → テーブルが大きいほどロック時間が長くなる
-- → その間、INSERTもSELECTもブロックされる
```

**CockroachDBのオンラインスキーマ変更：**

```
-- CockroachDBではこれが安全に実行できる
ALTER TABLE memories ADD COLUMN importance_score FLOAT;
-- → テーブルロックなし
-- → ダウンタイムなし
-- → クエリレイテンシへの影響なし
-- → バックグラウンドで段階的にスキーマが適用される
```

CockroachDBの内部では、スキーマ変更をデータベースジョブとして管理し、既存データへの影響を最小化しながら段階的に適用する。アプリの成長に合わせてDBを安全に進化させられる。

### 4. PostgreSQL互換——既存の資産がそのまま使える

CockroachDBはPostgreSQLワイヤプロトコル互換のため、既存のPostgreSQLドライバ・ORM・ツールをほぼそのまま使える。

`memory-server.js`での接続例：

```
// node-postgresをそのまま使用
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // CockroachDBでもこれだけでOK
  ssl: { rejectUnauthorized: false }
});
```

対応ドライバ・ORM：

| 言語 | ドライバ / ORM |
| --- | --- |
| Node.js | `pg`（node-postgres）、`node-postgres`、Drizzle ORM |
| Python | `psycopg2`、`asyncpg`、SQLAlchemy、Django ORM |
| Go | `pgx`、`database/sql` |
| ORM全般 | Prisma、Sequelize、TypeORM |
| CLI | `psql`コマンドで接続可能 |

PostgreSQLを使ったことがあれば、ほぼ学習コストゼロでスタートできる。ベンダーロックインのリスクも低く、`pg_dump`でデータの移行が現実的にできる。

### 5. Serializable Isolationがデフォルト

AIエージェントの記憶システムにとって、データの整合性は非常に重要だ。

CockroachDBはSerializable Isolation（直列化可能分離レベル）をデフォルトとして採用している。これはACID特性の中でも最も厳格な分離レベルだ。

```
【分離レベルの比較】

Read Uncommitted  →  Dirty Readが起きる（AIが古い/不正な記憶で行動）
Read Committed    →  Non-repeatable Readが起きる
Repeatable Read   →  Phantom Readが起きる
Serializable      →  完全な整合性（CockroachDBのデフォルト）← ここ
```

Cockroach Labs公式が「AIエージェントのメモリインフラ」として推進する根拠の一つが、この強整合性設計だ。AIエージェントが古い記憶や矛盾したデータで行動すると、カスケード障害（誤った判断が連鎖する問題）が起きる。Serializableがデフォルトであることは、記憶基盤として根本的に重要な特性だ。

---

## ベクター検索の仕組み——コードサンプル付き

Claushでは埋め込みモデルとして**gemini-embedding-001**を使用している。このモデルは3072次元のベクトルを出力し、テキストの意味を高精度で数値化する。

### スキーマ定義

```
-- CockroachDBでのメモリテーブル
CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id UUID NOT NULL,
  content TEXT NOT NULL,
  summary TEXT,
  -- gemini-embedding-001は3072次元
  embedding VECTOR(3072),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ベクター検索インデックス（v25.2以降のC-SPANN）
CREATE VECTOR INDEX ON memories (embedding);

-- キャラクターIDによる絞り込み用インデックス
CREATE INDEX ON memories (character_id, created_at DESC);
```

### 記憶の保存（埋め込み生成 + INSERT）

```
async function saveMemory(characterId, content, summary) {
  // Gemini APIで埋め込みベクトルを生成
  const embeddingResponse = await geminiClient.embedContent({
    model: 'gemini-embedding-001',
    content: { parts: [{ text: content }] }
  });
  const embedding = embeddingResponse.embedding.values;

  // CockroachDBに保存
  await pool.query(
    `INSERT INTO memories (character_id, content, summary, embedding)
     VALUES ($1, $2, $3, $4::vector)`,
    [characterId, content, summary, JSON.stringify(embedding)]
  );
}
```

### 記憶の検索（セマンティック検索）

```
async function searchMemories(characterId, query, limit = 5) {
  // クエリテキストを埋め込みベクトルに変換
  const queryEmbedding = await generateEmbedding(query);

  // コサイン距離でセマンティック検索
  const result = await pool.query(
    `SELECT content, summary, created_at,
            1 - (embedding <=> $2::vector) AS similarity
     FROM memories
     WHERE character_id = $1
     ORDER BY embedding <=> $2::vector
     LIMIT $3`,
    [characterId, JSON.stringify(queryEmbedding), limit]
  );

  return result.rows;
}
```

`<=>` 演算子でコサイン距離を計算し、意味的に類似した記憶を上位から返す。「昨日のランチ」というクエリに対して、「ラーメン」「昼食」「外食」に関する記憶が引き出せる。

---

## Claushでの設定手順

### 1. CockroachDB Cloudのアカウント作成

[CockroachDB Cloud](https://cockroachlabs.cloud/) にアクセスし、無料アカウントを作成する。

### 2. Basicクラスターの作成

1. 「Create Cluster」→「Basic」を選択
2. クラウド・リージョンを選択（日本ユーザーはAWS ap-northeast-1 東京を推奨）
3. クラスター名を入力して作成

### 3. 接続文字列の取得

クラスター作成後に表示される接続文字列をコピーする。

```
postgresql://user:password@xxxx.aws-ap-northeast-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full
```

### 4. Claushのメモリ設定

Claushアプリのサーバー設定画面で以下を設定する。

| 設定項目 | 値 |
| --- | --- |
| Memory DB | PostgreSQL |
| DATABASE\_URL | 上記の接続文字列 |
| Embedding Provider | gemini（オプション） |
| Embedding API Key | Gemini APIキー（オプション） |
| Embedding Dimension | 3072（gemini-embedding-001の場合） |

Embedding設定を追加することで、会話記憶のセマンティック検索（意味で検索）が有効になる。

---

## まとめ——比較表

| 観点 | SQLite（ローカル） | CockroachDB |
| --- | --- | --- |
| VPS乗り換え時のデータ | 消える | 残る（クラウド管理） |
| バックアップ | 手動 | 自動（マネージド） |
| 可用性 | VPSの可用性に依存 | 99.99%（SLA） |
| RPO | バックアップ間隔に依存 | 0秒 |
| RTO | 手動復旧（時間単位） | 9秒以内（自動） |
| ベクター検索 | （claush非対応） | 対応（pgvector互換） |
| スキーマ変更 | ダウンタイムあり | ダウンタイムなし |
| 分離レベル | Serializable | Serializable（デフォルト） |
| 無料枠 | ファイルサイズ制限のみ | 月50M RU + 10GiB |
| 設定の手軽さ | 非常に簡単 | やや手間（初回のみ） |

CockroachDBは「無料で使えるからとりあえず選ぶDB」ではない。AIエージェントの記憶基盤として技術的に理にかなった選択だ。

* **データロスがない**（RPO=0・Raft複製）
* **ベクター検索とトランザクションが1DBで完結**（pgvector互換・C-SPANN）
* **本番でのスキーマ変更が安全**（オンラインスキーマ変更）
* **既存資産がそのまま使える**（PostgreSQL互換）
* **個人開発で十分な無料枠**（月50M RU + 10GiB）

これらが揃って初めて「AIエージェントの記憶基盤として推せるDB」になる。

---

## 関連記事

**Claushアプリ**
