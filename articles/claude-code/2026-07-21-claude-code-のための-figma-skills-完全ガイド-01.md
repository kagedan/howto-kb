---
id: "2026-07-21-claude-code-のための-figma-skills-完全ガイド-01"
title: "Claude Code のための Figma Skills 完全ガイド"
url: "https://note.com/isaot/n/nc80174218fe9"
source: "note"
category: "claude-code"
tags: ["claude-code", "MCP", "OpenAI", "note"]
date_published: "2026-07-21"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

**Skills（スキル）**とは、Claude に一般的なタスクを確実かつ一貫して実行させるための、あらかじめ用意された指示セットです。

プロダクトデザインでは、多くの作業が定型的なため、Skills は特に効果を発揮します。例えば、

といった作業を効率化できます。

## Figma公式（ネイティブ）Skills

これらの Skills は、Claude Code 用の **Figma プラグイン**をインストールすると利用できます。まず、以下のコマンドでプラグインをインストールします。

```
claude mcp add figma
```

次に、Claude Code を自分の Figma アカウントと接続します。

```
/plugin
```

その後、以下を確認してください。

ここでいう **MCP（Model Context Protocol）** は、Claude Code が Figma を操作するための通信プロトコルです。これによって Claude は Figma のデザインを読み書きできるようになります。

それでは、このプラグインに含まれる主要な Skills を見ていきましょう。

---

## figma-use

**figma-use** は、Figma の読み書きを行うための基本となる Skill です。以下のような操作で自動的に呼び出されます。

例えば、既存のデザインシステムの Button や Card を参照して、新しい画面を生成する場合にも利用されます。

### ワンポイント

「この Skill が何をするのか知りたいけれど、SKILL.md を開くのは面倒」という場合は、

Claude Code 上で Skill 名をそのまま入力するだけで、代表的な利用例を表示してくれます。

---

## figma-generate-design

名前の通り、**Figma に新しいデザインを生成するための専用 Skill**です。

Claude Code をデザインのソースとして利用し、その内容を Figma に書き出す際に使われます。プロンプトは非常にシンプルです。

```
[作りたいものを説明]figma.com/design/new?node-id=%
```

実行すると Claude は

> "Figma に作成してよいですか？"

という確認を一度だけ行います。承認するとデザイン生成が始まります。この処理では

* figma-generate-design
* figma-use

の両方が呼び出されます。これは正常な動作です。生成後、新しいデザインが Figma 上に作成されます。

## figma-use-figjam

FigJam 用の中核 Skill です。Claude は以下のような要素を作成・編集できます。

* Sticky Notes
* Sections
* Connectors
* Shapes
* Tables
* Code Blocks
* Planning Boards
* Diagram
* Brainstorm

例えば SWOT 分析を作成したい場合は、

```
/figma-use-figjam create a SWOT for OpenAI
https://www.figma.com/board/new?node-id=%
```

と入力するだけです。すると Claude が FigJam 上に編集可能な SWOT 図を生成します。

## figma-generate-diagram

この Skill は、文章・仕様書・コード・設計資料などから、**編集可能な FigJam ダイアグラム**を生成します。対応する図の例

* フローチャート
* シーケンス図
* ER図
* 状態遷移図
* ガントチャート

例えば

```
show a pipeline diagram for food retailer
```

と入力すると、Claude は FigJam にパイプライン図を生成します。ユーザーフロー図なども自動生成可能です。

## figma-use-slides

Figma Slides 用の Skill です。以下のような操作ができます。

* スライド作成
* スライド編集
* セクション整理
* テーマ適用
* テキスト更新
* 図形追加
* Speaker Notes の追加

Claude Code の便利な点は、同じ情報を

* Figma Design
* FigJam
* Figma Slides

へ自由に変換できることです。例えば、先ほど FigJam に作成した SWOT をそのままプレゼン資料にしたい場合は、

```
/figma-use-slides turn this information into slides and post it here
https://www.figma.com/slides/xxxxx
```

と入力するだけで、Figma Slides の資料として出力されます。

---

## figma-code-connect

Code Connect は**Figma のコンポーネントと実際のソースコードを結び付ける仕組み**です。開発者は Dev Mode から

などをクリックするだけで、実装コードへ直接ジャンプできます。デザインと実装のズレを減らす非常に便利な機能です。ただし利用には

が必要です。

## コミュニティ製 Figma Skills

公式 Skills 以外にも、デザイン作業を効率化する優れた Community Skills が公開されています。

ここでは特におすすめのものを紹介します。

この Skill は既存デザインを解析し、デザインシステムのコンポーネントへ適切に置き換えます。これにより**Figma のデザインと Claude Code の実装との差を最小限に抑えられます。**

こちらはデザインシステムとの整合性を監査する Skill です。  
例えば

といった問題を検出します。すでにデザインシステムを運用しているチームであれば、**apply-design-system**と**audit-design-system**は必須と言えるでしょう。これにより本番品質（Production Ready）の UI を構築しやすくなります。

この Skill はAI エージェントから**デザインシステムのドキュメントを自動生成**します。  
例えば「この Button コンポーネントをドキュメント化して」と指示すると、Claude は

* Markdown (.md) の仕様書
* Component Spec
* Annotation Frame

を生成し、その内容を Figma に注釈付きで反映してくれます。デザインシステムのドキュメント作成まで自動化できます。

---

##
