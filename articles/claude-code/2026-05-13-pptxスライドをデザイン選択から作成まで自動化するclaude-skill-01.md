---
id: "2026-05-13-pptxスライドをデザイン選択から作成まで自動化するclaude-skill-01"
title: "pptxスライドをデザイン選択から作成まで自動化するclaude skill"
url: "https://zenn.dev/james_san/articles/e63776c8dd725f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "cowork", "zenn"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-rss"
query: ""
---

## はじめに

業務効率化のためにスライドのデザイン選択からコンテンツの計画、pptxのスライド生成までを自動で実行するためのclaudeスキル（coworkではproject指示文）を作成しました。本スキルの仕様や操作フローを本記事で整理しましたので、自由に使ってもらえれば幸いです。

## この記事から得られること

* Claudeの標準pptxスキルでできること・できないことの整理がわかる
* デザイン選択からスライド生成・保存までを一括で操作できるカスタムスキルが手に入る（Claude Cowork・Claude Codeの2パターン）
* 実際の操作フローと、動作に必要な設定変更によりすぐに利用できる
* カスタマイズして自分だけのスライドデザインも作れるようになる

---

# 第1部：背景 — なぜカスタムスキルが必要か

## Claudeの標準pptxスキルとは

Claude Codeには `anthropic-skills:pptx` という**Claude Code専用**の組み込みスキルが存在します。これはpptxgenjs（Node.js）のAPIリファレンスを内包しており、「.pptxファイルに関わるあらゆる操作」をトリガーに自動で有効化されます。PowerPointファイルの生成・編集・読み込みといった処理を実行する際のベースラインとして機能するスキルです。

## 標準スキルだけでは足りない理由

`anthropic-skills:pptx` は汎用スキルであるため、以下のフローには対応していません。

* デザインテンプレートをGUI上で選んでJSONとして出力する
* スライド構成案をClaudeに提示させ、ユーザーが確認・承認してから生成を開始する
* 生成した .pptxを所定のディレクトリ（`slide_store/`）に自動保存する

「スライドを作って」と一言伝えるだけで、デザイン確認 → 構成案提示 → 生成 → 保存まで一貫して動くフローは、標準スキルだけでは実現できません。そこで、このカスタムスキル `pptx-from-design` が役立ちます。

---

# 第2部：セットアップ

私のリポジトリを共有します。クローンして、使いたいパターンに応じたセットアップを行います。

```
git clone https://github.com/james-san-arigatou/slide-design-and-generation-tool.git
```

クローン後のディレクトリ構成：

```
slide-design-and-generation-tool/
├── design_selector.html        # デザイン選択・JSON出力UI
├── claude_cowork/
│   └── project_instruction.md  # Claude Cowork用 プロジェクト指示書
├── claude_code/
│   └── pptx-from-design/
│       └── SKILL.md            # Claude Code用 カスタムスキル
├── slide_store/                 # 生成されたスライドの出力先
└── package.json                 # pptxgenjs 依存関係
```

どちらのパターンも出力は **.pptx形式**です。違いは使用する環境です。ブラウザ上のclaude.aiで手軽に使いたければ **パターンA（Claude Cowork）**、ローカルのCLIツールとして使いたければ **パターンB（Claude Code）** を選んでください。

## パターンA：Claude Cowork

Claude Coworkは[claude.ai](https://claude.ai)のプロジェクト機能を使う方法です。ローカルへのツールインストールは不要で、ブラウザ上でセットアップが完結します。

1. claude.aiで **New Project** を作成する
2. `claude_cowork/project_instruction.md` の内容をプロジェクトの **Project Instructions** フィールドにそのまま貼り付ける
3. `project_instruction.md` 内のフッター設定を自分の名前に変更する（詳細は第4部）

## パターンB：Claude Code

Claude Codeを使ってPowerPointファイルをローカルに直接生成するパターンです。ローカルリポジトリを想定しています。pptxgenjsをNode.jsでローカル実行するため、事前準備が必要です。

**① 依存パッケージのインストール**

リポジトリのルートで実行します。

**② SKILL.md の配置**

`claude_code/pptx-from-design/SKILL.md` を Claude Code のスキルディレクトリにコピーします。

```
# Windows
C:\Users\<ユーザー名>\.claude\skills\pptx-from-design\SKILL.md

# Mac / Linux
~/.claude/skills/pptx-from-design/SKILL.md
```

配置後はパスとフッターの設定変更が必要です（詳細は第4部）。

---

# 第3部：実際のフロー

セットアップ完了後の操作フローは両パターン共通です。

## Step 1：デザインを選ぶ

`design_selector.html` をブラウザで開き、下記のように表示されているデザインテンプレートの中から好みのものをクリックして選択します。  
![](https://static.zenn.studio/user-upload/dfe6da298992-20260513.png)

## Step 2：デザインJSONを出力・提出する

選択後に表示される **「Export JSON」** ボタンを押してJSONファイルをダウンロードし、その内容をClaudeとのチャットに貼り付けます。このJSONにはカラー・フォント・レイアウト情報が含まれており、Claudeはこれを元にデザインを再現します。  
![](https://static.zenn.studio/user-upload/c183c3ef93ff-20260513.png)

## Step 3：テーマとコンテンツを伝える

デザインJSONと合わせて、スライドの内容を自由記述で伝えます。以下のような情報があるほど精度が上がります。

* プレゼンのテーマと目的
* 想定するオーディエンス
* 伝えたい主要メッセージ
* 含めたいデータ・グラフ・数値

## Step 4：構成案を確認・承認する

Claudeがスライド構成案を以下の形式で提示します。OKであれば「confirmed」と返すと生成が始まります。

```
Design applied: [デザイン名]
Total slides: [N]

| # | Headline | 概要 | Notes |
|---|----------|------|-------|
| 1 | ...      | ...  | ...   |
```

グラフを含むスライドがある場合、この段階でデータソースの確認が求められます。

## Step 5：生成・保存

承認後、Claudeが自動でスライドを生成し `slide_store/` ディレクトリに保存します。

```
slide_store/[design.id]-[topic-slug]-[YYYY-MM-DD].pptx
```

---

# 第4部：正しい動作のために必要な設定変更

## パターンA（Claude Cowork）のカスタマイズ

`project_instruction.md` 内の以下の行を自分の名前に書き換えます。

```
- Footer left: "made by [Your Name]"
                         ↓
- Footer left: "made by 山田太郎"
```

## パターンB（Claude Code）のカスタマイズ

**① 作業ディレクトリの設定（必須）**

SKILL.md 内の `<TOOL_DIR>` をリポジトリをクローンした絶対パスに置き換えます。

```
# 変更前
`<TOOL_DIR>`

# 変更後（例）
`C:\Users\<ユーザー名>\projects\slide-design-and-generation-tool\`
```

絶対パスが必要な理由：Claude Codeはスキル実行時にNode.jsスクリプトを一時ファイルとして書き出して実行します。このとき作業ディレクトリや出力先の特定に絶対パスが必要です。相対パスはClaude Codeの起動ディレクトリに依存するため、意図しない場所にファイルが生成されることがあります。

**② フッター名（著者名）の設定**

環境変数で設定する方法（推奨）と、SKILL.mdを直接編集する方法の2択があります。

```
# Windows (PowerShell) — 環境変数で設定
$env:SLIDE_AUTHOR = "山田太郎"
```

```
// SKILL.md を直接編集する場合
const AUTHOR = process.env.SLIDE_AUTHOR || "山田太郎";  // ← ここを変更
```

---

# 第5部：本PPT作成ツールの仕様について知っておくべきこと

## スライド枚数

枚数は規定していません。Claudeがコンテンツの量と構造を判断して自動で決定します。「1スライド1メッセージ」の原則を守りながら生成するため、内容が多いほど枚数も増えます。枚数を絞りたい場合は、Step 3でコンテンツを提示する際に10枚程度までは問題なく動作することを確認しています。

## スライドサイズ

サイズは **16:9固定** です。`design_selector.html` のデザインが16:9を前提に設計されているため、4:3や縦型には対応していません。両パターンともPowerPoint標準の16:9（10インチ × 5.625インチ）で出力されます。

## 日本語コンテンツへの対応

日本語・英語どちらのコンテンツにも対応しています。両パターンとも、デザインJSONにLatin系フォント（Didot・Futuraなど）が指定されていても、日本語コンテンツに対しては自動的に日本語互換フォント（Yu Mincho・Meiryo）へ置き換えて文字化けを防ぎます。

---

# 第6部：design\_selector.html のカスタマイズ方法

デザイン選択ツールである、design\_selector.htmlは私が事前に作成したツールですが、もちろんカスタマイズ可能です。  
例えば、Claudeを使って下記のように、自分の好きなデザインの画像イメージとdesign\_selector.htmlを添付してデザインを追加してもらうだけです。

![](https://static.zenn.studio/user-upload/60e6731d1b40-20260513.png)

---

## まとめ

`anthropic-skills:pptx` はClaude Code専用のpptx生成スキルですが、デザイン選択・構成案確認・ファイル保存を一貫して管理するフローは備えていません。今回紹介したカスタムスキル `pptx-from-design` はその差分を補い、「スライドを作って」の一言から保存まで完結するワークフローを実現します。

claude.aiのCoworkとClaude CodeのCLIという2パターンを用意しており、どちらも同じ .pptx形式で出力します。セットアップはリポジトリのクローンとフッター設定のみ（Claude Codeはパス設定も必要）。まずは `design_selector.html` を開いて、好みのデザインを選んでみてください。

最後に本スキルで作成したスライドの一例をお見せします。Executive Slateデザインで作成したものです。  
![](https://static.zenn.studio/user-upload/d30fd39c50fa-20260513.png)

---

最後までお読みいただきありがとうございます。  
参考になった方は、ぜひ「スキ」やフォローをお願いします。励みになります！  
もっといい方法がございましたら是非コメントいただけると嬉しいです！

#ClaudeCode #ClaudeCowork#Claude #AI活用 #PowerPoint #スライド作成 #開発効率化 #個人開発
