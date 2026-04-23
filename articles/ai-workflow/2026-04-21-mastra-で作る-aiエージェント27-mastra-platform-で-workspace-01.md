---
id: "2026-04-21-mastra-で作る-aiエージェント27-mastra-platform-で-workspace-01"
title: "Mastra で作る AIエージェント(27) Mastra Platform で Workspace 機能を動かす"
url: "https://zenn.dev/shiromizuj/articles/b7692eb3e87c80"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

[Mastra で作る AI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第27回です。

---

[第25回](https://zenn.dev/shiromizuj/articles/9ccd85865dca81)では Mastra Platform にプロジェクトをデプロイするところまで試しました。[第26回](https://zenn.dev/shiromizuj/articles/3ed824b8d97648)では会話履歴や RAG のストレージを LibSQL / DuckDB から外部の PostgreSQL サービス（Neon）に切り替えました。

今回は、[第15回](https://zenn.dev/shiromizuj/articles/25f8de31d22ddf) で取り上げた「Mastra Workspaces」機能を **Mastra Platform 上で動かす**ことに挑戦します。Workspace 機能のおさらいも兼ねて、サンドボックス（コード実行）と ワークスペース検索（Grep / BM25 / Vector）の 2 本立てで進めます。

## Workspace 機能のおさらい

第15回で詳しく解説しましたが、Mastra の Workspace は「エージェントがファイルを読み書きし、コマンドを実行し、検索もできる」機能です。構成要素は以下の 3 つです。

| 機能 | 概要 |
| --- | --- |
| **ファイルシステム** | ファイルの読み取り・書き込み・一覧・削除・コピー・移動・検索（Grep） |
| **サンドボックス** | シェルコマンドの実行、スクリプト実行、バックグラウンドプロセス管理 |
| **検索** | BM25（キーワード）/ ベクトル（意味）/ ハイブリッド検索 |

<https://zenn.dev/shiromizuj/articles/25f8de31d22ddf>

ローカル開発環境（`npm run dev` で起動する localhost:4111）では問題なく動作していたこれらの機能が、Platform 上でもちゃんと動くのか、確かめていきましょう。

---

## BEFORE: Workspace エージェントの準備

まず、ローカルで動いていた Workspace エージェントの定義を示します。

### `agents/workspace-agent.ts`（初期版）

```
import { Agent } from '@mastra/core/agent';
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';

const workspace = new Workspace({
  filesystem: new LocalFilesystem({
    basePath: './agent-workspace',
  }),
  sandbox: new LocalSandbox({
    workingDirectory: './agent-workspace',
  }),
});

export const workspaceAgent = new Agent({
  id: 'workspace-agent',
  name: 'Workspace Agent',
  instructions: `
あなたはローカルワークスペースにアクセスできる、有能な開発アシスタントです。
ワークスペース内でファイルの読み書き・管理、およびシェルコマンドの実行が可能です。

利用可能な機能:
- **ファイルシステム**: ファイル・ディレクトリの読み取り、書き込み、一覧表示、削除、コピー、移動、および内容の検索 (grep)
- **サンドボックス**: シェルコマンドの実行、スクリプトの実行、バックグラウンドプロセスの管理

ガイドライン:
- ファイルの削除や上書きなど、元に戻せない操作を行う前は必ず確認を取ること
- コードを書く際は、適切な拡張子とディレクトリ構造でファイルを作成すること
- ファイルパスは可能な限り相対パスを使用すること
- 時間のかかるコマンドはバックグラウンドモードの使用を検討すること
- コマンドの実行結果はわかりやすく要約して伝えること

ワークスペースのベースディレクトリは './agent-workspace' です。安全のため、すべてのファイル操作はこのディレクトリ内に制限されています。
`,
  model: 'openai/gpt-5.4',
  workspace,
});
```

この定義で Platform にデプロイし、Studio を確認すると Workspace Agent が登録されていることが分かります。

![](https://static.zenn.studio/user-upload/89ffba0ade0c-20260417.png)  
*Mastra Studio の Agents 一覧。Weather Agent、RAG Agent に加えて Workspace Agent が表示されている*

---

## サンドボックス機能を試す

### プロンプト

まずはサンドボックス（コード実行）機能を試します。LLM 単体では正確に答えにくい数学的な問題を投げてみましょう。

```
素因数として7,11,13,17,19 のみをもつ4桁の数字をすべて洗い出してください
```

### 結果：3 回目でようやく成功

エージェントはサンドボックスツール（Execute Command）を 3 回呼び出し、最終的に正しい答えにたどり着きました。

![](https://static.zenn.studio/user-upload/62e9fd25481d-20260417.png)  
*1 回目と 2 回目の試行。いずれもエラーで失敗している*

![](https://static.zenn.studio/user-upload/9d4e293082b6-20260417.png)  
*3 回目の試行で Node.js に切り替え、正しい結果（39 個）を得た*

最終的な回答は「4 桁で、素因数が **7, 11, 13, 17, 19 のみ** からなる整数は次の **39 個** です」。正しい答えです。

しかし、なぜ 1 発で成功しなかったのでしょうか。Traces を確認して原因を追ってみましょう。

### 1 回目の失敗：パスの二重化

![](https://static.zenn.studio/user-upload/e184d01151b1-20260417.png)  
*1 回目のツール呼び出し。`cwd` が `"./agent-workspace"` になっている*

![](https://static.zenn.studio/user-upload/8d09199fcb93-20260417.png)  
*Traces で確認したエラー内容。パスが二重化して ENOENT が発生*

エラーメッセージはこうです。

```
The "cwd" option is invalid: /home/daytona/app/agent-workspace/agent-workspace
ENOENT: no such file or directory, stat '/home/daytona/app/agent-workspace/agent-workspace'
spawn /bin/sh ENOENT
```

`workspace-agent.ts` では以下のように設定していました。

```
filesystem: new LocalFilesystem({ basePath: './agent-workspace' }),
sandbox:    new LocalSandbox({ workingDirectory: './agent-workspace' }),
```

Platform 上（`/home/daytona/app`）では、`LocalSandbox` の `workingDirectory: './agent-workspace'` が **LocalFilesystem の `basePath` を基準に解決** されます。その結果、パスが二重化しました。

```
/home/daytona/app/agent-workspace   ← basePath
              + agent-workspace     ← workingDirectory（相対パス）
= /home/daytona/app/agent-workspace/agent-workspace  ← 存在しない！
```

このディレクトリが存在しないため、シェル自体の起動（spawn）が失敗し、コマンドの内容以前に実行環境が作れませんでした。

### 2 回目の失敗：Python が使えない

![](https://static.zenn.studio/user-upload/bcb225214908-20260417.png)  
*2 回目のツール呼び出し。`cwd` が `"."` に修正されている*

![](https://static.zenn.studio/user-upload/b85ab443d610-20260417.png)  
*Traces で確認したエラー内容。python3 が見つからない*

1 回目の `cwd` 問題はエージェント自身が修正しましたが、今度は別のエラーです。

```
/bin/sh: 1: python3: not found
Exit code: 127
```

Exit code 127 は Unix/Linux で「コマンドが見つからない」を意味する標準的なエラーコードです。**Mastra Platform（Daytona サンドボックス）には Python がインストールされていない** ため、Python スクリプトは実行できません。

### 3 回目の成功：Node.js で実行

![](https://static.zenn.studio/user-upload/83398aa9fa6d-20260417.png)  
*3 回目のツール呼び出し。Node.js（`node`コマンド）で実行し、成功*

エージェントは 2 回の失敗を踏まえて、Python から **Node.js** に切り替えました。Platform のサンドボックスには Node.js がインストールされているため、今度は正常に実行できました。

### Platform サンドボックスの制約まとめ

| 制約 | 詳細 |
| --- | --- |
| **ランタイム** | Node.js のみ。Python / Ruby / Go 等はコンテナイメージに含まれず、別途インストールも不可 |
| **`workingDirectory` の解決** | `LocalSandbox` の `workingDirectory` は `LocalFilesystem.basePath` 相対で解決される。同じパスを指定するとパスが二重になる |

### 回避策：`workingDirectory` の修正

`LocalSandbox` の `workingDirectory` には `'.'` を指定することで、`basePath` 内のルートを正しく参照できます。

```
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './agent-workspace' }),
  sandbox: new LocalSandbox({ workingDirectory: '.' }),  // basePath 内のルートを指す
});
```

今回はエージェントが自力でリトライして解決しましたが、最初からこの設定にしておけば 1 回目の失敗は防げます。

---

## ワークスペース検索機能を試す

サンドボックスが動いたところで、次は検索機能を試していきます。Grep → BM25 → ベクトル検索の順に段階的に有効化していきます。

### Phase 1: Grep 検索

現在の `workspace-agent` には `LocalFilesystem` が設定済みなので、**Grep 検索は何も追加せずにそのまま使えます**。先ほどのサンドボックスの実験で使ったワークスペースに対して、すぐに試してみましょう。

ファイルを書き込み、Grep で検索する一連の流れを確認します。

![](https://static.zenn.studio/user-upload/74a732f5d84a-20260417.png)  
*ファイルの作成と Grep 検索の結果。`mastra_workspace_write_file` でファイルを書き込み、`mastra_workspace_grep` で検索*

ツールの詳細を見ると、`write_file` でファイルを作成し、`grep` で文字列を検索していることが分かります。

![](https://static.zenn.studio/user-upload/eb84d3e6221b-20260417.png)  
*`mastra_workspace_write_file` ツールの詳細。`sample.md` に内容を書き込み*

![](https://static.zenn.studio/user-upload/18e04457cf3d-20260417.png)  
*`mastra_workspace_grep` ツールの詳細。パターン `"エージェント"` で検索し、1 件ヒット*

Grep 検索は文字列の完全一致で探すシンプルな検索です。コード検索、ログ検索、識別子検索などに向いています。

---

### Phase 2: BM25 検索

BM25 検索を有効にするには、`workspace-agent.ts` に `bm25: true` を追加するだけです。外部サービスは不要です。

```
const workspace = new Workspace({
  filesystem: new LocalFilesystem({ basePath: './agent-workspace' }),
  sandbox: new LocalSandbox({ workingDirectory: '.' }),
  bm25: true,
  autoIndexPaths: ['/'],  // basePath以下を自動インデックス
});
```

デプロイして BM25 検索を試してみます。

![](https://static.zenn.studio/user-upload/b1805799f872-20260417.png)  
*BM25 検索の実験。エージェントがテスト用ファイルを作成・インデックス化し、BM25 モードで検索を実行*

エージェントにテスト用ファイルの作成・インデックス化・検索を一気にやってもらいました。`mastra_workspace_mkdir` でディレクトリを作成し、`mastra_workspace_write_file` でファイルを書き込み、`mastra_workspace_index` でインデックスに登録し、最後に `mastra_workspace_search` で BM25 検索を実行しています。

![](https://static.zenn.studio/user-upload/4a39fef87096-20260417.png)  
*Platform 上の Workspace に作成されたファイル。Workspace の Files ビューから確認できる*

BM25 検索は**キーワードの一致度**でランキングする検索です。Grep より柔軟ですが、同義語や言い換えには弱いという特性があります。

---

### Phase 3: ベクトル検索

ベクトル検索は BM25 と違い、**外部のベクトルストアとエンベディングモデル**が必要です。Platform 上のストレージはエフェメラル（揮発性）なので、ベクトルデータの保存先としては使えません。

そこで、[第26回](https://zenn.dev/shiromizuj/articles/3ed824b8d97648)で構築済みの **Neon（PgVector）** と **OpenAI の text-embedding-3-small** をそのまま流用します。

### `agents/workspace-agent.ts`（最終版）

```
import { Agent } from '@mastra/core/agent';
import { ModelRouterEmbeddingModel } from '@mastra/core/llm';
import { Workspace, LocalFilesystem, LocalSandbox } from '@mastra/core/workspace';
import { PgVector } from '@mastra/pg';
import { LibSQLVector } from '@mastra/libsql';
import { Memory } from '@mastra/memory';
import { embed } from 'ai';

/** ベクトルインデックス名（固定値で管理） */
const WORKSPACE_SEARCH_INDEX = 'workspace_agent_search';
/** text-embedding-3-small の次元数 */
const WORKSPACE_EMBEDDING_DIMENSION = 1536;

// DATABASE_URL が設定されている場合は Neon（PgVector）、なければ LibSQL（ローカル SQLite）を使用
const workspaceVectorStore = process.env.DATABASE_URL
  ? new PgVector({
      id: 'workspace-vector',
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false },
    })
  : new LibSQLVector({
      id: 'workspace-vector',
      url: 'file:./workspace-vectors.db',
    });

/** 起動時にベクトルテーブルを作成（冪等: 既存なら何もしない） */
try {
  await workspaceVectorStore.createIndex({
    indexName: WORKSPACE_SEARCH_INDEX,
    dimension: WORKSPACE_EMBEDDING_DIMENSION,
  });
} catch (error) {
  console.warn('[workspace-vector] createIndex failed at startup (will retry on first use):', error);
}

const embeddingModel = new ModelRouterEmbeddingModel('openai/text-embedding-3-small');

const workspace = new Workspace({
  filesystem: new LocalFilesystem({
    basePath: './agent-workspace',
  }),
  sandbox: new LocalSandbox({
    workingDirectory: '.',
  }),
  bm25: true,
  autoIndexPaths: ['/'],
  searchIndexName: WORKSPACE_SEARCH_INDEX,
  vectorStore: workspaceVectorStore,
  embedder: async (text: string) => {
    const { embedding } = await embed({
      model: embeddingModel,
      value: text,
    });
    return embedding;
  },
});

export const workspaceAgent = new Agent({
  id: 'workspace-agent',
  name: 'Workspace Agent',
  instructions: `
あなたはローカルワークスペースにアクセスできる、有能な開発アシスタントです。
ワークスペース内でファイルの読み書き・管理、およびシェルコマンドの実行が可能です。

利用可能な機能:
- **ファイルシステム**: ファイル・ディレクトリの読み取り、書き込み、一覧表示、削除、コピー、移動、および内容の検索 (grep)
- **サンドボックス**: シェルコマンドの実行、スクリプトの実行、バックグラウンドプロセスの管理
- **BM25 検索**: ワークスペース内のファイルをキーワード検索（インデックスからの高速全文検索）
- **ベクトル（意味）検索**: 自然言語クエリで意味的に類似したファイルを検索
- **ハイブリッド検索**: BM25 とベクトル検索を組み合わせた高精度検索（デフォルトモード）

ガイドライン:
- ファイルの削除や上書きなど、元に戻せない操作を行う前は必ず確認を取ること
- コードを書く際は、適切な拡張子とディレクトリ構造でファイルを作成すること
- ファイルパスは可能な限り相対パスを使用すること
- 時間のかかるコマンドはバックグラウンドモードの使用を検討すること
- コマンドの実行結果はわかりやすく要約して伝えること
- ファイルを新規作成・更新したあとは index_content ツールでインデックスに登録すること

検索モードの選び方:
- **bm25**: 完全一致・技術用語・コード検索に適している
- **vector**: 概念クエリ・自然言語表現に適している（例：「エラー処理のベストプラクティス」）
- **hybrid**: 多くの場合に最適（BM25 と vector を組み合わせる）

ワークスペースのベースディレクトリは './agent-workspace' です。安全のため、すべてのファイル操作はこのディレクトリ内に制限されています。
`,
  model: 'openai/gpt-5.4',
  workspace,
  memory: new Memory({
    options: {
      lastMessages: 30,
    },
  }),
});
```

ポイントは以下です。

* `DATABASE_URL` 環境変数があれば Neon（PgVector）、なければ LibSQL を使うように分岐させています。ローカル開発と Platform デプロイで同じコードを使い回せます
* `embedder` に OpenAI の `text-embedding-3-small` を指定し、ベクトル化を行います
* `bm25: true` と `vectorStore` の両方を設定しているため、BM25 / ベクトル / ハイブリッドのすべての検索モードが利用可能です

### Grep / BM25 / Vector の比較実験

3 つの検索モードがすべて有効になったので、その違いが分かる実験をしてみます。以下のプロンプトを投げました。

```
現在、Workspaces機能のうち、Grep検索とBM25検索とVector検索のすべてが有効になっています。
Grep検索とBM25検索とVector検索の違いが分かるような実験をしてみたいです。
この実験に役立つようないくつかのファイルを作ったうえでインデックス化し、実験を進めてください。
```

エージェントは自律的に実験用コーパスを作成し、インデックス化し、比較検索を実行してくれました。

![](https://static.zenn.studio/user-upload/cd7b4c82507a-20260417.png)  
*エージェントが自律的に実験用ファイルを作成・インデックス化し、比較検索を実行している*

![](https://static.zenn.studio/user-upload/f0f4b69a5778-20260417.png)  
*実験結果のレポート。作成したファイルの一覧と検索結果の比較が出力されている*

![](https://static.zenn.studio/user-upload/3e7909aeb8c6-20260417.png)  
*Grep / BM25 / Vector の検索結果比較。同じクエリでも返ってくる結果が異なることが分かる*

### 実験結果のハイライト

エージェントが作成した実験用ファイルは、日本語・英語・同義表現・厳密語・コード断片を混ぜた 8 つのファイルです。いくつかの代表的なクエリで検索した結果から、特に違いが鮮明に出たケースを紹介します。

#### クエリ: `rate limiting`

| 検索方式 | 結果 |
| --- | --- |
| **Grep** | 文字列 `rate limiting` を**実際に含むファイル**のみヒット（3 件） |
| **BM25** | ほぼ同様に**語の一致が強い文書**が上位（3 件） |
| **Vector** | 上記 3 件に加え、`05_code_example.ts` など**完全一致がなくても意味的に近い文書**も返した |

#### クエリ: `アクセス過多 上限超過 再試行待ち`（日本語の言い換え表現）

| 検索方式 | 結果 |
| --- | --- |
| **Grep** | `02_synonyms_ja.txt` のみ（その語が書いてある文書だけ） |
| **BM25** | **0 件**（語が一致しないと弱い） |
| **Vector** | 意味的に近い **5 件**を返した（英語の rate limiting 系や日本語の意味的近傍も含む） |

このケースが最も違いが鮮明です。

#### クエリ: `システム保護のため受付を遅らせる`

| 検索方式 | 結果 |
| --- | --- |
| **Grep** | `08_japanese_semantic.txt` のみ（その表現が書いてある） |
| **BM25** | **0 件** |
| **Vector** | 5 件（英語の throttling / rate limiting 系まで拾った） |

この日本語表現は、英語の "slow down clients"、"rate limiting"、"throttling" と**意味的には近い**ですが文字列は全然違います。Grep / BM25 では弱く、Vector では強い——という違いがきれいに出ています。

### 3 つの検索方式の使い分け

実験結果をまとめると、以下のような使い分けが見えてきます。

| 検索方式 | 特徴 | 向いている場面 |
| --- | --- | --- |
| **Grep** | 文字列の完全一致。速くて分かりやすい | コード検索、ログ検索、エラーコード、関数名、識別子 |
| **BM25** | キーワードの一致度でランキング。Grep より柔軟 | 技術文書検索、仕様書、エラーメッセージ |
| **Vector** | 意味の近さで検索。言い換え・別言語にも対応 | 概念検索、FAQ、「どう表現されているか分からない」情報探し |

---

## 考察：Platform で Workspace 機能を使う際の注意点

### サンドボックスの制約

今回の実験で分かった Platform サンドボックスの制約を改めて整理します。

* **Node.js のみ実行可能**。Python / Ruby / Go などは使えません
* **`workingDirectory` は `'.'` に設定する**のが安全。`basePath` と同じ値を指定するとパスが二重化します
* エージェントは失敗を踏まえて自律的にリトライしてくれますが、最初から正しく設定しておくに越したことはありません

### ファイルシステムの揮発性

Mastra Platform（Daytona サンドボックス）のファイルシステムは**エフェメラル**（**揮発性**）です。コンテナが再起動されるたびにリセットされます。

今回のデモでは、エージェントの処理の中でワークスペースにファイルを作成してインデックス化しました。これは「エージェントが会話の中で一時的にファイルを使う」用途には十分ですが、**外部から定期的にファイルを格納する**（例：GitHub リポジトリと同期を取るなど）といった用途には向きません。`LocalFilesystem` のままでは、Platform コンテナ内部のパスに外部からアクセスする方法がないためです。

### 外部ストレージの検討

永続的なファイルストレージが必要な場合は、外部ストレージの利用が推奨されます。

* **Grep / BM25 検索** にファイルシステムが必要なら → **S3 / GCS Filesystem** を利用
* **ベクトル検索** なら → 今回のように**外部 PostgreSQL サービス（Neon + pgvector）** を利用

サンドボックスについては、Daytona 以外にも E2B や Blaxel などの選択肢があります。詳しくはこちらの記事を参照してください。  
<https://zenn.dev/shiromizuj/articles/e05b0f22d60c10>

### そもそも Platform を使うべきか？

Workspace 機能が中心となるエージェント——つまりファイルの永続化やファイル検索が主要なユースケースであるエージェントの場合、**Mastra Platform ではなく AWS の EC2 + EBS、あるいは ECS + EFS で運用する**ことを選んだ方が素直かもしれません。

Platform はエージェントの手軽なデプロイ・運用に優れていますが、ファイルシステムの永続性が求められるワークロードでは、従来型のインフラの方が適しているケースがあります。用途に応じて使い分けましょう。

---

## まとめ

今回は Mastra Platform 上で Workspace 機能（サンドボックス + 検索）を動かしてみました。

* **サンドボックス**: Platform 上では Node.js のみ実行可能。`workingDirectory` のパス設定に注意が必要
* **Grep 検索**: 追加設定なしですぐ使える
* **BM25 検索**: `bm25: true` を追加するだけで有効化。外部サービス不要
* **ベクトル検索**: 外部のベクトルストア（Neon + pgvector）とエンベディングモデルが必要
* **Platform の制約**: ファイルシステムは揮発性。永続化が必要なら外部ストレージを検討する

Platform でサクッとデプロイできる手軽さと、Workspace 機能の制約を天秤にかけて、自分のユースケースに合った構成を選ぶことが大切です。
