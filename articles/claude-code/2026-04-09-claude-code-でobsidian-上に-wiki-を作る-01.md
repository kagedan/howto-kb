---
id: "2026-04-09-claude-code-でobsidian-上に-wiki-を作る-01"
title: "Claude Code で、Obsidian 上に Wiki を作る"
url: "https://zenn.dev/wfukatsu/articles/a70a311f5a7b51"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

Andrej Karpathy が提唱した **LLM Wiki パターン**（LLM にソースドキュメントを読ませ、構造化された wiki ページを自動生成・維持させる手法）を **Obsidian プラグイン + Claude Code スキル** として実装した話です。

実際にプロジェクト資料 15 本を食わせて **28 ページの wiki** を自動生成し、品質監査まで回した結果を交えて解説します。

### 対象読者

* Obsidian でナレッジ管理をしているが「書く気力がない」方
* LLM を「おしゃべり相手」以上に使いたいエンジニア
* Karpathy の LLM Wiki パターンに興味があるが実装方法がわからない方

### できあがるもの

ソースドキュメントを `sources/` に置いて Ingest を実行すると、こうなります。

```
vault/
├── sources/          ← 生のソースドキュメント（不変）
├── wiki/             ← LLM が生成・維持する wiki ページ群
│   ├── summary-*.md  ← ソースの要約
│   ├── entity-*.md   ← 人物・組織・ツール
│   └── concept-*.md  ← アイデア・技法・理論
├── schema.md         ← wiki の構造・規約定義
├── index.md          ← カテゴリ別カタログ
└── log.md            ← 操作の時系列ログ
```

---

## 背景 — なぜ LLM Wiki なのか

### Karpathy のアイデア

2025 年、Karpathy は「LLM を使ってパーソナル wiki を維持する」パターンを提案しました。

<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

核心は以下の分業です。

* **人間**: ソースのキュレーションと戦略的思考に集中する
* **LLM**: 面倒な「帳簿付け」（要約、相互リンク、カテゴリ整理）を担う

### 既存ツールの課題

Obsidian は強力なノートアプリですが、「知識を構造化する作業」は依然として人力です。記事を読んでメモを取り、タグを付け、リンクを張る — この作業が面倒で放置される。結局ノートは溜まるが「知識ベース」にはならない。

LLM Wiki パターンはこの問題を根本から解決します。**ソースを投げ込むだけ**で、LLM が勝手に構造化してくれる。

---

## 三層アーキテクチャと三つの操作

### 三層構造

| レイヤー | 役割 | 編集者 |
| --- | --- | --- |
| `sources/` | 生のソースドキュメント。不変 | 人間 |
| `wiki/` | 構造化された wiki ページ群 | LLM |
| `schema.md` + `index.md` + `log.md` | wiki のメタデータ | LLM |

人間はソースを置くだけ。wiki の中身には手を出さない。この分離が重要です。

### 三つの操作

| 操作 | 入力 | 出力 |
| --- | --- | --- |
| **Ingest** | ソースドキュメント 1 つ | summary + entity + concept ページ群（10〜15 ページ） |
| **Query** | 自然言語の質問 | wiki 内容に基づいた回答（synthesis ページとして保存可能） |
| **Lint** | なし（wiki 全体をスキャン） | ヘルススコア + 問題リスト + 修正提案 |

---

## 実装 — Obsidian プラグインとして作る

### 技術スタック

```
TypeScript + Obsidian Plugin API + Anthropic Claude API
```

ビルドは esbuild、型チェックは tsc。ファイル構成は以下の通りです。

```
src/
├── main.ts       # プラグインエントリ: コマンド登録、各種モーダル
├── settings.ts   # 設定画面（API キー、モデル、ディレクトリ）
├── llm.ts        # Anthropic SDK ラッパー
├── ingest.ts     # Ingest パイプライン
├── query.ts      # Query パイプライン
├── lint.ts       # Lint パイプライン
└── types.ts      # 共有型定義
```

### データフロー（全操作共通）

三つの操作は全て同じパターンに従います。

LLM への指示は全て **JSON 出力を要求** します。これにより、レスポンスをそのまま解析してファイル操作に落とし込めます。

### Ingest の実装（核心部分）

Ingest は最も複雑な操作です。以下がシステムプロンプトの概要です。

src/ingest.ts

```
const INGEST_SYSTEM = `You are a wiki maintainer.
You receive a source document and the current state of a personal wiki.
Your job is to ingest the source into the wiki by:
1. Writing a summary page for the source
2. Creating or updating entity/concept pages that the source touches
3. Adding cross-references ([[wiki links]]) between pages
4. Keeping pages factual and well-structured in markdown

Respond with a JSON object:
{
  "summary": "Brief description of what was ingested",
  "pages": [
    {
      "path": "wiki/page-name.md",
      "action": "create" | "update",
      "content": "Full markdown content including frontmatter"
    }
  ],
  "indexEntry": "Line to add to index.md",
  "logEntry": "Line for log.md"
}`;
```

ポイントは **既存 wiki ページの先頭 10 行をコンテキストとして渡す** ことです。これにより、LLM は既存ページとの重複を避け、適切にクロスリファレンスを張れます。

src/ingest.ts

```
// 既存 wiki ページの先頭10行を収集してコンテキストに含める
const wikiFiles = app.vault.getFiles()
  .filter(f => f.path.startsWith(settings.wikiDir + "/"));
const wikiIndex: string[] = [];
for (const f of wikiFiles) {
  const content = await app.vault.read(f);
  const firstLines = content.split("\n").slice(0, 10).join("\n");
  wikiIndex.push(`--- ${f.path} ---\n${firstLines}`);
}
```

既存ページの更新時は、**2 回目の LLM 呼出でマージ** します。

src/ingest.ts

```
async function mergeContent(llm, existing, newContent) {
  const system = `You merge wiki page content.
Preserve existing information while incorporating new facts.
Resolve contradictions by preferring newer information.`;
  return await llm.call(system, 
    `## Existing\n${existing}\n\n## New\n${newContent}`);
}
```

---

## Claude Code スキルとしても動く

Obsidian プラグインとは別に、**Claude Code のスラッシュコマンド** としても同じ操作を提供しています。

```
/wiki-init                        # vault 構造の初期化
/wiki-ingest                      # ソース取り込み
/wiki-query "Claude Codeの使い方"   # wiki への質問
/wiki-lint                        # 品質監査
```

Obsidian プラグインは GUI 操作、Claude Code スキルは CLI 操作。**同じ vault に対してどちらからでも操作できます**。

---

## 実際に使ってみた — 15 本のソースから 28 ページの wiki を自動生成

### やったこと

「AI 駆動開発・内製化定着支援プログラム」の資料（14 週分 + 全体概要 = 15 本）を wiki に取り込みました。

### Step 1: Ingest（ソース取り込み）

15 本のソースに対して `/wiki-ingest` を実行。結果:

| 種別 | 件数 | 例 |
| --- | --- | --- |
| Summary | 15 | 各週の要約ページ |
| Entity | 2 | ScalarDB、Scalar Inc. |
| Concept | 11 | Software 2.0、インテント・エンジニアリング、DDD、Atomic Design など |
| **合計** | **28 ページ** |  |

1 本のソースから平均 5〜8 ページが生成・更新されます。ソースが増えるほど「更新」が増え、既存ページが充実していきます。

### Step 2: Lint（品質監査）

28 ページの wiki に対して `/wiki-lint` を実行。

```
Health Score: 76/100

Issues:
- ORPHAN PAGES (11件): 週別サマリーが他ページからリンクされていない
- MISSING CROSS-REFERENCES (8件): 関連ページ間のリンク不足
- INCONSISTENT ALIAS (1件): 誤ったリンクテキスト
```

### Step 3: Auto-fix（自動修正）

Lint が検出した問題を自動修正。

* 概要ページに全 15 週へのリンクを追加
* 8 箇所の不足クロスリファレンスを追加
* エイリアスの修正

```
Health Score: 76 → 92/100
```

### Step 4: Query（質問）

wiki に対して「Claude Code の使い方」を質問。28 ページを横断して統合された回答が返ってきました。週別の活用パターン、プロンプトの書き方、注意点まで — 元のソースドキュメント単体では得られない **横断的な知識** です。

---

## 詰まったポイント・Tips

---

## まとめ

* **Karpathy の LLM Wiki パターン**を Obsidian プラグイン + Claude Code スキルとして実装した
* ソースを投げ込むだけで、要約・エンティティ・コンセプトページが自動生成される
* Lint で品質監査、Query で横断検索。**wiki は使うほど賢くなる**
* 15 本のソースから 28 ページ、ヘルススコア 92/100 の wiki が自動で育った

「ノートを溜めるだけで知識ベースにならない」問題に悩んでいる方は、LLM に帳簿付けを任せてみてください。人間は読むものを選ぶだけでいい — それが LLM Wiki のコアアイデアです。

ソースコードは GitHub で公開しています。

<https://github.com/wfukatsu/obsidian-wiki>
