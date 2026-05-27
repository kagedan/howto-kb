---
id: "2026-05-26-mastra-announce-mastra-skills-発表-コーディングエージェントに-mas-01"
title: "[Mastra Announce] Mastra Skills 発表 ― コーディングエージェントに Mastra の知識を与える仕組み"
url: "https://zenn.dev/shiromizuj/articles/37cc4521c7674e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-26"
date_collected: "2026-05-27"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

※やや昔のアナウンスをさかのぼって記事にしています

---

2026年2月5日、Mastra は **Mastra Skills** についてのアナウンスを行いました。これは 2月4日発表の、Mastra Ver1.2 で公開された機能で、コーディングエージェントが Mastra を使った開発を支援するために必要なコンテキストを、構造化されたナレッジファイルの形で提供するものです。

---

## 背景

### コーディングエージェントにとっての「ツール情報提供」の難しさ

Claude Code や Cursor、GitHub Copilot などのコーディングエージェントを使って開発するとき、エージェントが利用しているライブラリの最新情報を持っているとは限りません。トレーニングデータのカットオフ以降に登場した API や仕様変更については、エージェントは知識を持っていません。

そのため、開発者はしばしば「システムプロンプトにドキュメントを貼り付ける」「README を都度コンテキストに渡す」といった手作業を行います。しかしこれにはコンテキストウィンドウの消費という問題が伴います。全ドキュメントを一度に渡すと、それだけで数万〜数十万トークンを消費し、実際の会話に使えるコンテキストが圧迫されます。

### 従来の解決策: MCP Docs Server

Mastra はこれまで **MCP Docs Server** を提供してきました。これは Model Context Protocol (MCP) を介してエージェントがオンデマンドでドキュメントを参照できる仕組みです。ドキュメント照会の精度が高く、特にマイグレーションガイドなど高度なツールとの連携に強みがあります。

一方で、MCP サーバーを別途起動・設定する手間があり、純粋なドキュメント参照だけが目的の場合にはオーバースペックになることがあります。

### Agent Skills 仕様の登場

Mastra Skills は [Agent Skills 仕様](https://agentskills.io/specification) に準拠して設計されています。Agent Skills は、エージェントに知識を提供するための標準フォーマットを定義するオープンな仕様です。

仕様の核心は **プログレッシブ・ディスクロージャー（段階的開示）** というアーキテクチャ原理です。エージェントがスキルを読み込む際、全情報を一度に取得するのではなく、必要に応じて必要な分だけ取得します:

| 段階 | 内容 | 想定トークン数 |
| --- | --- | --- |
| 1. メタデータ | `name` と `description` フィールド — エージェント起動時に全スキル分読み込まれる | 約 100 トークン |
| 2. 指示 | `SKILL.md` 本文 — スキルが有効化されたときのみ読み込まれる | 推奨 5,000 トークン以内 |
| 3. リソース | `scripts/`, `references/`, `assets/` 内のファイル — 必要なときのみ読み込まれる | オンデマンド |

この設計により、エージェントは「今何が必要か」に応じて自律的に情報を取得し、コンテキストウィンドウを効率的に活用できます。

---

## ニュースリリースの内容

### 発表の概要

* **日時**: 2026年2月5日
* **著者**: Lennart Jörgens（Mastra ソフトウェアエンジニア）
* **発表内容**: Mastra Skills のリリース。コーディングエージェントに Mastra の知識を与える構造化ナレッジファイル。

### 同時に行われた改善

この発表と合わせて、以下のドキュメント関連の改善も行われました:

* **[Build with AI](https://mastra.ai/docs/getting-started/build-with-ai) セクションの新設**: AI コーディングエージェントを使って Mastra をビルドするためのガイドを集約した新しいドキュメントセクション
* **Markdown URL**: 任意のドキュメントページに `.md` を付けると Markdown 形式で取得できるように（例: `mastra.ai/docs/agents/overview.md`）
* **`llms.txt` の改善**: `text/markdown` ヘッダーの処理を含む生成ロジックの改善

---

## 具体的な掘り下げ

### Mastra Skills の中身

現在提供されている Mastra スキルは 1 つで、プログレッシブ・ディスクロージャーを使って Mastra に関する包括的な情報を提供します。含まれる内容は以下の通りです:

| カテゴリ | 内容 |
| --- | --- |
| セットアップ & インストール | `npm create mastra` の使い方、手動インストール手順、Kitchen-sink サンプル |
| 組み込みドキュメント参照 | 各パッケージの `node_modules` に同梱されたドキュメントの参照方法 |
| リモートドキュメント参照 | [mastra.ai/docs](https://mastra.ai/docs) の参照方法（フォールバック） |
| トラブルシューティング | よくある問題とその解決方法 |
| マイグレーション | 旧バージョンから最新バージョンへの移行方法 |

スキルの定義は GitHub の [mastra-ai/skills](https://github.com/mastra-ai/skills) で公開されています。

### `npx skills` による追加方法

Mastra Skills の導入は 1 コマンドで完了します:

```
npx skills add mastra-ai/skills
```

`npx skills` は Agent Skills 仕様に対応したスキルをエージェント環境に追加するための CLI ツールです。`npm create mastra` で新しいプロジェクトを作成する際のオプションとしても追加されました。

### 組み込みドキュメント (Embedded Docs) との関係

Mastra Skills の前から、Mastra には「組み込みドキュメント」という仕組みがありました。`@mastra/core` などすべての Mastra パッケージは、`node_modules` 内に独自のドキュメントを同梱しています。

```
cat node_modules/@mastra/core/dist/docs/SKILL.md
```

この `dist/docs/` フォルダは Agent Skills 仕様に準拠した構造になっており、エージェントが直接参照できます。Mastra Skills（リモートのナレッジファイル）と組み込みドキュメント（パッケージに同梱のローカルファイル）は補完関係にあります。

### Mastra Skills と MCP Docs Server の使い分け

| 用途 | 推奨 |
| --- | --- |
| ドキュメント参照全般 | **Mastra Skills** |
| バージョン間のマイグレーション支援 | **MCP Docs Server** |
| オフライン / シンプルな設定 | **Mastra Skills**（設定が最小限） |
| 高度な検索・照合が必要 | **MCP Docs Server** |

Mastra が「純粋なドキュメント目的なら Skills を推奨」と述べている背景には、Skills のセットアップの容易さと、プログレッシブ・ディスクロージャーによるコンテキスト効率の高さがあります。

### Agent Skills 仕様の SKILL.md フォーマット

参考までに、Agent Skills 仕様が定める `SKILL.md` の基本フォーマットは以下の通りです:

```
---
name: skill-name              # 必須。小文字英数字とハイフンのみ、64文字以内
description: >                # 必須。スキルの目的と使う場面を記述、1024文字以内
  このスキルが何をするか、いつ使うかを記述する。
license: Apache-2.0           # 任意。ライセンス名
metadata:                     # 任意。追加のキー・バリュー情報
  author: mastra-ai
  version: "1.0"
---

# スキル本文（Markdown 形式）
エージェントへの指示、使い方の例、エッジケースなど
```

スキルのディレクトリ構造:

```
skill-name/
├── SKILL.md           # 必須
├── scripts/           # 任意: エージェントが実行可能なスクリプト
├── references/        # 任意: 詳細なリファレンスドキュメント
└── assets/            # 任意: テンプレートや静的リソース
```

---

## まとめ

Mastra Skills は、「エージェントに最新のツール知識をコンテキスト効率よく提供する」という課題に対するひとつの回答です。Agent Skills 仕様の採用により、Mastra 固有の仕組みではなく、より広いエコシステムの一部として機能します。

コーディングエージェントを使って Mastra ベースのアプリケーションを開発している場合、以下の 1 コマンドで試すことができます:

```
npx skills add mastra-ai/skills
```

詳細は公式ドキュメントの [Build with AI](https://mastra.ai/docs/getting-started/build-with-ai) セクションを参照してください。
