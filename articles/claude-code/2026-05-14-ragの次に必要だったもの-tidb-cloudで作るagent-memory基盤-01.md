---
id: "2026-05-14-ragの次に必要だったもの-tidb-cloudで作るagent-memory基盤-01"
title: "RAGの次に必要だったもの: TiDB Cloudで作るAgent Memory基盤"
url: "https://zenn.dev/yushiyamamoto/articles/tidb-agent-memory-lab"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "OpenAI", "TypeScript", "zenn"]
date_published: "2026-05-14"
date_collected: "2026-05-15"
summary_by: "auto-rss"
query: ""
---

## この記事で作るもの

RAGだけでは、AIエージェントの運用で落としたくない記憶を取り逃がします。

たとえば `ignorePublish` や `published:false` のような運用トークンは、意味が近いだけではなく、文字列として正確に拾う必要があります。一方で「公開前に人間が確認する」「Claude Codeのレビューで検索漏れを防ぐ」のような記憶は、意味検索で拾いたい。

つまり、Agent Memoryには **意味検索と正確一致の両方** が必要でした。

実際に困るのは、次のような記憶です。

* このリポジトリでは production deploy の前に preview URL を見る
* Zenn記事は `published: false` のままレビューする
* Qiitaでは `ignorePublish: true` をローカルに残す
* 特定の顧客案件では、送信なし、人間レビュー必須にする

これらは普通のRAGで扱う「文書チャンク」と少し性質が違います。意味が近いだけでは足りず、`ignorePublish`、`MEM9_API_KEY`、ファイル名、CLIコマンドのような正確なトークンも落とせません。

そこでこの記事では、TiDB Cloud上に **Codex / Claude Code / 人間メモを横断するAgent Memory基盤** を作ります。

実装はGitHubで公開しています。

<https://github.com/YushiYamamoto/agent-memory-lab>

## この記事の要点

* 作ったもの: TiDB Cloud上に、ベクトル検索、全文検索、SQLメタデータ絞り込み、RRF統合をまとめたAgent Memoryの最小実装です。
* なぜTiDBか: Agent Memoryでは「意味が近い記憶」と `ignorePublish` のような正確な運用トークンを、同じSQL基盤で同時に拾う必要があるためです。
* 持ち帰れる知見: RAGの精度問題は検索モデルだけではなく、記憶のスキーマ、検索方式の組み合わせ、運用ゲートの残し方でかなり変わります。

リポジトリ構成は次の通りです。

![agent-memory-labの実装ファイル構成](https://static.zenn.studio/user-upload/deployed-images/95c9fd8c71e6b13d38ff3737.png?sha=9fc081a416b0322f18ae8f329c46b7ac4d3b1d4e)

```
/Users/yushiy/agent-memory-lab
├── src/
│   ├── embedding.ts
│   ├── local-store.ts
│   ├── tidb-store.ts
│   ├── fusion.ts
│   └── cli.ts
├── data/sample-memories.jsonl
└── tests/
```

## なぜTiDBを使うのか

Agent Memoryには、少なくとも3種類の検索が必要です。

| 欲しい検索 | 例 | ベクトル検索だけだと |
| --- | --- | --- |
| 意味検索 | 「公開前に確認する運用ルール」 | 得意 |
| 正確な文字列検索 | `ignorePublish`, `published:false` | 取り逃がすことがある |
| メタデータ絞り込み | `project = "zenn-docs"` | SQLと一緒に扱いたい |

TiDBはMySQL互換のSQLデータベースでありながら、ベクトル検索と全文検索を同じ基盤で扱えます。TiDBのドキュメントでは、`VECTOR`型、`VEC_COSINE_DISTANCE()`、全文検索の `FTS_MATCH_WORD()`、そしてハイブリッド検索が紹介されています。

今回作成したTiDB Cloudインスタンスは次の設定です。

```
name: agent-memory-lab
plan: Starter
region: Singapore (ap-southeast-1)
spending limit: $0/month
status: Active
TiDB version: v8.5.3
```

実際にTiDB Cloud上でも、StarterプランのインスタンスがActiveになっていることを確認しました。

![TiDB Cloud上でagent-memory-labインスタンスがActiveになっている画面](https://static.zenn.studio/user-upload/deployed-images/57e44eb9bd994147180e091d.png?sha=d49e2fe66c6b960fc99d29e1a5cbc5c0c19207f4)

Singaporeを選んだ理由は、TiDB Cloudの全文検索が現在 `Frankfurt (eu-central-1)` と `Singapore (ap-southeast-1)` のServerless/Starter系リージョンで提供されているためです。

## テーブル設計

記憶は1テーブルに寄せます。

```
CREATE DATABASE IF NOT EXISTS `agent_memory_lab`;

CREATE TABLE IF NOT EXISTS `agent_memory_lab`.agent_memories (
  id VARCHAR(128) PRIMARY KEY,
  source VARCHAR(64) NOT NULL,
  agent VARCHAR(64) NOT NULL,
  project VARCHAR(255) NOT NULL,
  kind VARCHAR(64) NOT NULL,
  content TEXT NOT NULL,
  content_vec VECTOR(64) NOT NULL,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FULLTEXT INDEX ft_agent_memories_content (content) WITH PARSER MULTILINGUAL
);
```

ポイントは、`content_vec` と `FULLTEXT INDEX` を同じテーブルに持たせていることです。

`source` と `agent` は分けています。たとえば `source = "codex"` は記憶の発生元、`agent = "claude-code"` はその記憶を書いた実行主体です。ここをSQLで絞れるようにしておくと、「Codexが書いたClaude Code向けの注意」も扱えます。

## 埋め込みはあえて簡易実装にした

この記事の主役は埋め込みモデルの性能ではなく、検索の構造です。

そのため、サンプル実装では外部APIを呼ばず、文字列を64次元のハッシュベクトルに変換しています。

```
export function embedText(input: string, dimensions = 64): number[] {
  const vector = Array.from({ length: dimensions }, () => 0);
  for (const token of tokenize(input)) {
    const hash = fnv1a(token);
    const bucket = hash % dimensions;
    const sign = hash & 1 ? 1 : -1;
    vector[bucket] += sign * Math.log2(token.length + 1);
  }
  return normalize(vector);
}
```

本番ではOpenAI、Cohere、Jina AIなどの埋め込みに差し替えればよいです。ここでは、読者がAPIキーなしで検索パイプラインを再現できることを優先しました。

もちろん、ハッシュベクトルには限界があります。実際の埋め込みモデルのように文脈を深く理解するわけではなく、語彙の揺れや言い換えには弱いです。

それでも今回は、あえてこの形にしました。検証したかったのは「どの埋め込みモデルが強いか」ではなく、次の3点だからです。

* Agent MemoryをSQLテーブルとしてどう持つか
* 正確なトークン検索と意味検索をどう併用するか
* 2つの検索結果をRRFでどう統合するか

本番で使うなら、`embedText()` の内側だけを外部の埋め込みAPIに差し替え、`content_vec` の次元数と投入処理を合わせます。検索側の設計、つまり `project` や `agent` で絞ってからベクトル検索と全文検索を統合する流れは、そのまま残せます。

## 検索は2本走らせてRRFで混ぜる

検索は次の2本です。

```
-- vector search
SELECT id, content,
  VEC_COSINE_DISTANCE(content_vec, ?) AS distance
FROM `agent_memory_lab`.agent_memories
WHERE project = ?
ORDER BY distance
LIMIT ?;
```

```
-- full-text search
SELECT id, content,
  FTS_MATCH_WORD(?, content) AS score
FROM `agent_memory_lab`.agent_memories
WHERE FTS_MATCH_WORD(?, content)
  AND project = ?
ORDER BY score DESC
LIMIT ?;
```

最後に、2つの結果を Reciprocal Rank Fusion で統合します。

```
score += weight / (k + rank);
```

RRFを使う理由は単純です。ベクトル検索と全文検索ではスコアの尺度が違います。距離とBM25系スコアをそのまま足すより、順位を使って混ぜたほうが実装が壊れにくいです。

TiDBの `pytidb` でもハイブリッド検索の融合方法として `rrf` と `weighted` が説明されています。今回はTypeScriptからSQLを直接書くため、自前でRRFだけ実装しました。

## ローカルでも同じ失敗を再現する

TiDB接続情報がない読者でも試せるように、同じJSONLをローカル検索できます。

```
npm install
npm test
npm run typecheck
npm run build
npm run search -- --store local "ignorePublish published:false"
```

検証結果です。

![ローカルでtest、typecheck、buildが通った画面](https://static.zenn.studio/user-upload/deployed-images/d09fa81265bae2dc09450bb0.png?sha=3bba87feb893754de2b4a0e179e7327d40039220)

```
npm test
Test Files 5 passed
Tests 8 passed

npm run typecheck
passed

npm run build
passed
```

`ignorePublish published:false` で検索すると、最上位にZenn公開ゲートの記憶が返ります。

![ignorePublish published:falseの検索でZenn公開ゲートの記憶が最上位に出た画面](https://static.zenn.studio/user-upload/deployed-images/b903968970dcde402d6c5602.png?sha=7f68c7452091ad3cd0885b8b21d9f4b588fcb900)

```
{
  "id": "codex-zenn-skill-001",
  "project": "zenn-docs",
  "kind": "workflow",
  "content": "Zenn記事は published:false の下書きで作成し、npx zenn preview と git status を確認してから人間が公開する。"
}
```

このクエリは、ベクトル検索だけでなく全文検索が効く例です。`ignorePublish` と `published:false` は意味というより、正確な運用トークンだからです。

## TiDB Cloudで実行する

TiDB Cloudの接続情報を `.env` に入れます。パスワードはリポジトリに保存しません。

```
TIDB_HOST=gateway01.ap-southeast-1.prod.aws.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=<prefix>.root
TIDB_PASSWORD=<password>
TIDB_DATABASE=agent_memory_lab
TIDB_SSL_CA=/etc/ssl/cert.pem
MEMORY_STORE=tidb
```

実行コマンドです。

```
npm run doctor -- --store tidb
npm run seed -- --store tidb --sample
npm run search -- --store tidb "Claude Code の検索で ignorePublish を落としたくない" --project agent-memory-lab
```

DBパスワードを作らずにSQL Editorで試したい場合は、貼り付け用SQLを出力できます。

```
npm run --silent sql-editor > /tmp/agent-memory-lab.sql
npm run --silent rrf-sql > /tmp/agent-memory-lab-rrf.sql
```

`--silent` を付ける理由は、npmの実行ログをSQLファイルに混ぜないためです。`sql-editor` が出力するSQLは、データベース作成、`VECTOR(64)` カラム、`FULLTEXT INDEX ... WITH PARSER MULTILINGUAL`、サンプルデータ投入まで含んでいます。`rrf-sql` は、この記事の最後で使うRRF統合クエリを出力します。

このSQLにはパスワードやAPIキーを含めていません。

実際にTiDB CloudのSQL Editorに貼り付けて実行すると、`agent_memory_lab` データベースと `agent_memories` テーブルが作成され、サンプルデータを投入できます。

まず全文検索です。`ignorePublish published:false` のような正確な運用トークンを検索すると、Zenn公開ゲートの記憶が最上位に返りました。

```
USE agent_memory_lab;

SELECT id, project, kind,
  FTS_MATCH_WORD('ignorePublish published:false', content) AS fts_score,
  content
FROM agent_memories
WHERE FTS_MATCH_WORD('ignorePublish published:false', content)
ORDER BY fts_score DESC
LIMIT 5;
```

![TiDB Cloud SQL Editorで全文検索が正確な運用トークンを拾った結果](https://static.zenn.studio/user-upload/deployed-images/824442be880aa3987603915e.png?sha=1256730a919dd00de2a95f48f52e38f158edc273)

次にベクトル検索です。`Claude Code の検索で ignorePublish を落としたくない` というクエリをベクトル化して、`VEC_COSINE_DISTANCE()` で近い記憶を並べます。

```
USE agent_memory_lab;

SELECT id, project, kind,
  VEC_COSINE_DISTANCE(content_vec, '<query-vector>') AS vector_distance,
  content
FROM agent_memories
WHERE project IN ('zenn-docs', 'agent-memory-lab')
ORDER BY vector_distance ASC
LIMIT 5;
```

![TiDB Cloud SQL EditorでVEC_COSINE_DISTANCEによるベクトル検索を実行した結果](https://static.zenn.studio/user-upload/deployed-images/de65082afcb656142972fc3a.png?sha=776d543b4212fbf37675b36e6cdb3728a0ce8dff)

この2つを別々に見ると、Agent Memoryで欲しい検索の性質が分かります。全文検索は `ignorePublish` や `published:false` のような落としたくない文字列に強く、ベクトル検索は「Claude Codeのレビュー」「検索漏れ」「TiDBの判断」のような近い意味の記憶を拾いやすい。だから最後は、どちらか一方ではなくRRFで統合します。

最後に、TiDB上で全文検索の順位とベクトル検索の順位をRRFで統合します。`FTS_MATCH_WORD()` はTiDBの制約上、`WHERE` と `ORDER BY` で使う形に寄せています。

```
USE agent_memory_lab;

WITH vector_hits AS (
  SELECT id, project, kind, content,
    ROW_NUMBER() OVER (
      ORDER BY VEC_COSINE_DISTANCE(content_vec, '<query-vector>') ASC
    ) AS vector_rank
  FROM agent_memories
  WHERE project IN ('zenn-docs', 'agent-memory-lab')
  ORDER BY VEC_COSINE_DISTANCE(content_vec, '<query-vector>') ASC
  LIMIT 5
),
fulltext_ordered AS (
  SELECT id, project, kind, content
  FROM agent_memories
  WHERE FTS_MATCH_WORD('ignorePublish published:false', content)
  ORDER BY FTS_MATCH_WORD('ignorePublish published:false', content) DESC
  LIMIT 5
),
fulltext_hits AS (
  SELECT id, project, kind, content,
    ROW_NUMBER() OVER () AS fulltext_rank
  FROM fulltext_ordered
),
fused AS (
  SELECT id, project, kind, content, vector_rank, NULL AS fulltext_rank FROM vector_hits
  UNION ALL
  SELECT id, project, kind, content, NULL AS vector_rank, fulltext_rank FROM fulltext_hits
)
SELECT id, project, kind,
  MIN(vector_rank) AS vector_rank,
  MIN(fulltext_rank) AS fulltext_rank,
  ROUND(SUM(
    IF(vector_rank IS NULL, 0, 1.0 / (60 + vector_rank)) +
    IF(fulltext_rank IS NULL, 0, 1.0 / (60 + fulltext_rank))
  ), 6) AS rrf_score
FROM fused
GROUP BY id, project, kind
ORDER BY rrf_score DESC
LIMIT 5;
```

結果を見ると、全文検索だけではなくベクトル検索にも出てくる記憶が上位に上がります。`codex-zenn-skill-001` と `codex-failure-005` が近いスコアで並ぶため、「公開ゲート」と「ベクトル検索だけでは正確トークンを落とす」という2つの運用記憶を同時に拾えています。

![TiDB Cloud SQL Editorで全文検索とベクトル検索をRRF統合した結果](https://static.zenn.studio/user-upload/deployed-images/2e5e904d0cf50774854ed640.png?sha=855db78de65807c5b740ef02053fa0ede7c9af9b)

## mem9との関係

mem9は、Agent Memoryを管理サービスとして提供する選択肢です。公式サイトでは、複数のエージェントスタックをまたいだ共有メモリ、ハイブリッド recall、ダッシュボード、TiDB Cloud上で動くことが説明されています。

今回の実装は、mem9の置き換えではありません。

むしろ役割は逆です。

* mem9: 運用を任せたいときの管理型メモリ
* この実装: Agent Memoryの検索設計を自分で理解するための最小構成

自作してみると、なぜ単なるベクトルDBでは足りないのか、なぜSQLメタデータが必要なのかが見えます。そのうえで、本番運用ではmem9のような管理型サービスを選ぶ判断もしやすくなります。

## この設計を業務で使うなら

この実装は小さな検証用ですが、業務のAgent Memoryに持ち込むなら、次の4点を最初から設計に入れます。

### 1. プロジェクトと顧客単位で記憶を分離する

Agent Memoryで怖いのは、検索精度よりも「別案件のルールを拾ってしまうこと」です。

そのため、本番では `project` だけでなく、`tenant_id`、`workspace_id`、`visibility` のような列を追加します。検索時も、いきなり全体からベクトル検索するのではなく、SQLの `WHERE` で対象範囲を絞ってから検索します。

```
WHERE tenant_id = ?
  AND workspace_id = ?
  AND visibility IN ('team', 'project')
```

Agent Memoryは「たくさん覚える」よりも、「使ってよい記憶だけを思い出す」ほうが重要です。

### 2. 長期記憶の劣化を前提にする

運用ルールは古くなります。

たとえば、ある時点では「Zenn記事は `published: false` のままレビューする」が正しくても、公開直前のワークフローでは `published: true` に変える必要があります。古い記憶が強く残りすぎると、AIエージェントは過去の正解で現在の作業を止めます。

本番では、記憶に次のような列を持たせます。

```
status: active | superseded | archived
confidence: 0.0 - 1.0
valid_from / valid_until
source_commit
```

検索結果に出す前に、古い記憶や置き換え済みの記憶を落とせるようにしておくと、Agent Memoryは運用しやすくなります。

### 3. コストは書き込み時と検索時で分けて考える

埋め込みAPIを使う場合、全部の検索で毎回コストを払う設計にすると続きません。

現実的には、記憶を書き込むタイミングで `content_vec` を作り、検索時はクエリだけをベクトル化します。さらに、`ignorePublish` や `MEM9_API_KEY` のような正確なトークンを含むクエリでは、全文検索を先に強く効かせます。

つまり、コストを下げる鍵は「全部をベクトル検索に寄せないこと」です。TiDBのようにSQL、全文検索、ベクトル検索を同じテーブルで扱えると、この調整がしやすくなります。

### 4. 検索評価を運用に組み込む

Agent Memoryは、作った直後よりも運用中に壊れます。

新しい記憶が増えると、以前は1位に出ていた重要ルールが3位や5位に落ちることがあります。だから、最初から小さな評価セットを持つべきです。

```
query: "Zenn 公開前に確認すること"
expected_top_ids:
  - codex-zenn-skill-001
  - codex-zenn-publish-guard-002
```

このようなゴールデンクエリを用意して、`precision@3` や「必須IDが上位に出るか」をCIで見ます。Agent Memoryの品質は、モデル単体ではなく、記憶の追加、検索、統合、評価を1つの運用ループにして初めて保てます。

## まとめ

AIエージェントの記憶は、普通のRAGよりも運用寄りです。

「意味が近い記憶」だけでなく、「この文字列だけは絶対に落とせない記憶」があります。

TiDB Cloudを使うと、次の3つを1つのSQL基盤で扱えます。

* ベクトル検索
* 多言語全文検索
* プロジェクトやエージェント単位のメタデータ絞り込み

今回の結論は、Agent Memoryでは **ベクトル検索か全文検索か** ではなく、**両方をSQLの中で統合すること** が重要だということです。

## 参考
