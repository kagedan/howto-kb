---
id: "2026-04-28-もうこれによりすることができますとは書かないclaudeaiでai臭を一掃するhumanizer-s-01"
title: "もう「これにより〜することができます」とは書かない：Claude.aiでAI臭を一掃するHumanizer Skill 3種【英語＋日本語対応】"
url: "https://qiita.com/4q_sano/items/d58476bf8fd846f4b3f8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-28"
date_collected: "2026-04-29"
summary_by: "auto-rss"
---

![ChatGPT Image Apr 28, 2026, 12_35_28 PM.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82835/7c7f6cb0-bdc6-4c7f-8e3f-a9807d3cdd4c.png)


## はじめに

Claude.aiのSkills機能を使うと、独自のワークフローや専門知識を後付けで追加できます。今回はその中から、AI生成テキスト特有の言い回しを検知して書き換えてくれるオープンソースSkill「Humanizer」シリーズの導入手順をまとめました。

英語版に加え、日本語コンテンツ向けの派生Skillも有志によって複数公開されています。3種類とも同じ手順でclaude.aiに入るので、それぞれの特徴と導入の流れをまとめて紹介します。

GitHubのREADMEはどれも「Claude Code向け」と書かれていますが、SKILL.md形式に準拠しているSkillはclaude.aiでもそのまま動作します。


## 3種類のHumanizer Skill

今回扱うのは次の3つです。すべてMITライセンスです。

| Skill | 言語 | 特徴 |
|-------|------|------|
| [`blader/humanizer`](https://github.com/blader/humanizer) | 英語 | 本家。Wikipedia「Signs of AI writing」ベースの29パターン |
| [`makotofalcon/humanizer-ja`](https://github.com/makotofalcon/humanizer-ja) | 日本語 | `blader/humanizer` のfork。日本語固有の25+パターンを3層構造で解析 |
| [`gonta223/humanizer-ja`](https://github.com/gonta223/humanizer-ja) | 日本語 | インスパイア系の独立実装。20パターン＋書き換え後の代替表現ガイド付き |

### blader/humanizer（英語版・本家）

| 項目 | 内容 |
|------|------|
| ライセンス | MIT |
| 検出パターン数 | 29種類 |
| ベース | Wikipedia「[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)」 |

代表的な検出パターンをいくつか挙げると、

- 大袈裟な意義づけ（`marking a pivotal moment in the evolution of...` のたぐい）
- em dash（`—`）の多用
- 3点並べる癖（`innovation, inspiration, and insights`）
- 迎合的なトーン（`Great question!` `You're absolutely right!`）
- 中身のない締め（`The future looks bright`）

このあたりが該当します。

### makotofalcon/humanizer-ja（日本語版・分析寄り）

| 項目 | 内容 |
|------|------|
| ライセンス | MIT |
| 検出パターン数 | 25+種類 |
| 構造化アプローチ | 3層構造（記号 → 語彙 → 思考） |

AI臭さを次の3層に分けて捉えるアプローチが特徴です。

| 層 | 内容 |
|---|---|
| 第1層 | 記号・書式の残骸（コロン、Markdown、絵文字） |
| 第2層 | 語彙・文体の偏り（「これにより」「包括的」など） |
| 第3層 | 思考構造の型（ポジション不在、体験の欠如、予定調和） |

検出される日本語のAIっぽい表現：

- 「これにより〜することができます」
- 「画期的な一歩を刻みました」
- 「浮き彫りにしており」「示唆しており」
- 漢語の連続（「促進・醸成・推進・構築」）
- 「課題はあるものの〜期待されます」のテンプレ結び

なぜAI臭くなるのか、構造から理解したい人向けです。

### gonta223/humanizer-ja（日本語版・実践寄り）

| 項目 | 内容 |
|------|------|
| ライセンス | MIT |
| 検出パターン数 | 20種類 |
| 特色 | 「消した後に何を入れるか」まで具体的に指示 |

「今すぐ使えるチェックリスト」を重視した設計で、執筆後の最終チェックに使いやすいです。検出カテゴリは5つあります。

- 語彙・表現（意義の過剰強調、定型評価語、カタカナ語の過剰使用、曖昧な出典）
- 構造・フォーマット（太字+コロン箇条書き、三点セット強制、全角ダッシュ乱用、見出しの過剰構造化）
- 文体・トーン（説教くさい前置き、接続詞の多用、否定並列構文、追従的トーン）
- 日本語固有（敬語の均一化、主語の過剰明示、「することができます」、体温のない結論）
- セルフ監査（冒頭・結論・二重チェック）

## 前提条件

導入前に以下を確認してください。

- Claude.aiのアカウント（Free / Pro / Max / Team / Enterprise すべてのプランで使えます）
- 「コード実行とファイル作成（Code execution and file creation）」が有効化されていること
  - `Settings > Capabilities` から有効化できます
- Team / Enterpriseプランの場合、Ownerが組織設定でSkillsを有効化していること

## 導入手順

3つのSkillはすべて同じ手順で入ります。ここでは `blader/humanizer` を例に進めますが、`makotofalcon/humanizer-ja` も `gonta223/humanizer-ja` も同じ流れです。

### Step 1: GitHubからZIPをダウンロード

各リポジトリのページにアクセスし、緑色の `Code` ボタン → `Download ZIP` を選びます。

![GitHubからhumanizerリポジトリをZIPでダウンロード](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82835/93dcc9d7-8d2d-4513-a4a8-6ef9eb7ad1d3.png)

ダウンロードされるZIPは以下のファイル名になりますが、リネームせずそのままclaude.aiにアップロードできます。

| Skill | ZIPファイル名 |
|-------|--------------|
| `blader/humanizer` | `humanizer-main.zip` |
| `makotofalcon/humanizer-ja` | `humanizer-ja-main.zip` |
| `gonta223/humanizer-ja` | `humanizer-ja-main.zip` |

SKILL.mdのfrontmatterに `name` フィールドが定義されているため、ZIP内のフォルダ名が `xxx-main` のままでもclaude.ai側では正しいSkill名で登録されます。

### Step 2: Claude.aiにアップロード

1. Claude.aiにログインし、左サイドバーから `カスタマイズ > スキル`（[claude.ai/customize/skills](https://claude.ai/customize/skills)）を開く
2. 右上の `+` ボタンをクリック
3. `+ スキルを作成` → `スキルをアップロード` を選択
4. ダウンロードしたZIPをそのままアップロード

### Step 3: 導入の確認

アップロードが終わるとSkill一覧に追加されます。トグルがONになっていれば使える状態です。

![Claude.aiのカスタマイズ画面でhumanizer Skillが有効化された状態](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82835/f8759b59-1f8f-4661-a580-f039992c46a7.png)

詳細画面では次のような情報が見られます（`blader/humanizer` の例）。

| 項目 | 値 |
|------|-----|
| Version | 2.5.1 |
| License | MIT |
| Compatibility | claude-code opencode |
| Allowed tools | Read, Write, Edit, Grep, Glob, AskUserQuestion |
| トリガー | スラッシュコマンド + 自動 |

`Compatibility` 欄が `claude-code opencode` になっていますが、これはSKILL.mdのfrontmatterに記載されているタグというだけで、claude.aiでの動作には影響しません。SKILL.md内のシステムプロンプトはclaude.aiでもちゃんと読み込まれます。

## 使い方

3つのSkillはどれも次の方法で呼び出せます。

### 方法1：自然言語で呼び出す

チャットで普通に依頼すれば、Claudeが状況に応じてHumanizerを起動してくれます。

```
以下の文章をhumanizeしてください：

[AI生成の文章を貼り付け]
```

### 方法2：スラッシュコマンド

入力欄で `/` を打つとSkill一覧が出てくるので、明示的に呼び出せます。`humanizer-ja` を直接指定したいときなどに便利です。

### 方法3：Voice Calibration（文体マッチング）

`blader/humanizer` には自分の文体に寄せて書き換える機能があります。サンプル文を一緒に渡してください。

```
以下は私の文体サンプルです：

[自分が書いた2〜3段落の文章]

この文体に合わせて、以下の文章をhumanizeしてください：

[書き換えたい文章]
```

文のリズムや語彙の癖、句読点の使い方を学習して反映してくれます。

## 動作例

### 英語コンテンツ（`blader/humanizer`）

Before：

> AI-assisted coding serves as an enduring testament to the transformative potential of large language models, marking a pivotal moment in the evolution of software development. In today's rapidly evolving technological landscape, these groundbreaking tools—nestled at the intersection of research and practice—are reshaping how engineers ideate, iterate, and deliver.

After：

> AI coding assistants can speed up the boring parts of the job. They're great at boilerplate: config files and the little glue code you don't want to write. They can also help you sketch a test, but you still have to read it.

過剰な装飾、em dash、3点並べ、`testament` や `landscape` のような抽象的なAI語彙が消えて、具体的な内容に変わっているのが分かります。

### 日本語コンテンツ（`humanizer-ja` 系）

Before：

> 本記事では、AIアシスタントを活用した開発フローについて包括的に解説していきます。これにより、開発者は効率的にコーディングを行うことができます。さらに、品質向上にも寄与することが期待されます。今後の展開が注目されます。

After：

> AIアシスタントを実務に投入して半年。最初は懐疑的だったが、コーディング速度は体感で2割上がった。一方で、レビューの粗さが目立つケースも出てきている。本記事では、その両面を実例ベースで整理する。

「これにより」「することができます」「期待されます」「今後の展開が注目されます」といった日本語のAI定型句が消え、「転」を含んだ構成に変わっています。

## 用途別の使い分け

3つのSkillは目的別に使い分けるのがおすすめです。

| 用途 | 推奨Skill |
|------|----------|
| 英文ブログ・README・ドキュメント | `blader/humanizer` |
| ソースコード内の英語コメント | `blader/humanizer` |
| 日本語記事の執筆前の構造設計 | `makotofalcon/humanizer-ja`（3層構造で構成チェック） |
| 日本語記事の執筆後の最終確認 | `gonta223/humanizer-ja`（チェックリスト方式で即修正） |
| 日英バイリンガル記事 | 3つを連続適用するパイプライン運用も可能 |

なお、日本語版2種を同時にインストールするとSKILL.mdの `name` フィールドが衝突する場合があるため、用途に合わせて1つ選んで導入する形がシンプルでおすすめです。

## まとめ

- Skillsはチャット版Claudeでも全プランで使える（コード実行の有効化が必要）
- 英語版・日本語版2種ともに、`Download ZIP` したZIPをそのままアップロードするだけで導入完了
- Claude CodeとClaude.aiで同じSkillを共有運用できるので、執筆環境をまとめやすい
- 用途や言語、執筆フェーズによって使うSkillを選び分けると効果的

書く言語と書く段階で使い分けるのが、結局いちばん運用しやすかったです。次は自分のQiita執筆スタイルに合わせてSKILL.mdをカスタマイズする話を書こうと思っています。

## 参考リンク

- [blader/humanizer (GitHub)](https://github.com/blader/humanizer)
- [makotofalcon/humanizer-ja (GitHub)](https://github.com/makotofalcon/humanizer-ja)
- [gonta223/humanizer-ja (GitHub)](https://github.com/gonta223/humanizer-ja)
- [Use Skills in Claude (公式ドキュメント)](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
