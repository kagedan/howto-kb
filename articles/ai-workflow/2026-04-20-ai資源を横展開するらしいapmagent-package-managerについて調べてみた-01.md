---
id: "2026-04-20-ai資源を横展開するらしいapmagent-package-managerについて調べてみた-01"
title: "AI資源を横展開するらしいAPM（Agent Package Manager）について調べてみた"
url: "https://zenn.dev/keru/articles/bc9bb6dda1a1ff"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

# AI資源を横展開するらしいAPM（Agent Package Manager）について調べてみた

## APM とは

APM（Agent Package Manager）は、**AI エージェントの設定・指示をパッケージ管理するツール**らしいです。  
Microsoft がオープンソースで開発しています。

公式曰く、npmやpipのような存在とのことです。

> Software teams solved dependency management for application code decades ago. npm, pip, cargo, go mod — declare what you need,  
> install it reproducibly, lock versions, ship.  
> AI agent configuration has no equivalent. Until now.

ドキュメントを読む限りは、「AI に読ませるルールやプロンプト」をパッケージとして管理・配布できるとのことでした。

個人開発で複数のAIを横断している人は、コンパイルで対応させることができますし、  
チーム開発を行なっている場合は、コーディング規約やツールをパッケージとして Git リポジトリに置き、  
メンバーは `apm install` 一発で取り込めるようになるようです。

### 使い方

例えばですが、

```
apm install myorg/coding-standards
```

これだけで、個々で作成していた資源が各ツール向けに配置され、Claude なら `.claude/` に、Copilot なら `.github/instructions/` という形で配布されるようです。  
<https://microsoft.github.io/apm/introduction/what-is-apm/#supported-tools>

また、`apm.yml` というファイルに「このプロジェクトで使うパッケージ」を書いておけば、  
新しくリポジトリをクローンした人も `apm install` だけで同じ状態になるようです。

npm の `package.json` と同じ感覚で利用できそうです。

```
# apm.yml
name: my-project
version: 1.0.0
dependencies:
  apm:
    - microsoft/apm-sample-package
    - anthropics/skills/skills/frontend-design
    - github/awesome-copilot/agents/api-architect.agent.md
```

<https://microsoft.github.io/apm/introduction/what-is-apm/#how-apm-works>

パッケージとしての管理に対応しているのはルール以外もあり、スラッシュコマンド形式の定型ワークフロー、特化した AI エージェントの定義も同様に配布できるようです。  
また MCP サーバーの依存関係も `apm.yml` に一緒にて管理できるとのこと。

## 何が統一・配布できるか

APMは依存解決、lock生成、ターゲットごとの形式変換、MCP設定、uninstall時の追跡削除も扱うようです。

パッケージリポジトリの `.apm/` ディレクトリにあるファイルを取り出し、使っているツールに応じた正しい場所にコピーします。

```
パッケージの .apm/instructions/coding-standards.md
  → Claude なら    .claude/rules/ にコピー
  → Copilot なら   .github/instructions/ にコピー
  → Cursor なら    .cursor/rules/ にコピー
```

<https://microsoft.github.io/apm/introduction/what-is-apm/#the-lifecycle>

### 対応しているもの

`apm install` でネイティブ配置できるprimitivesと、各ツールでの2026年4月時点での対応状況は以下のとおりです。

ここでいうprimitives名は、APM が複数の AI ツールを横断して扱うための分類名として記載します。  
各ツールが同じ名前で機能を提供しているわけではないので適正読み変えをしてください。

たとえば APM の `instructions` は、Copilot では custom instructions、  
Claude では rules や `CLAUDE.md`、Cursor では rules といった、それぞれのツールのネイティブな仕組みに対応します。

| primitives | 役割 | Copilot | Claude | Cursor | OpenCode | Codex | Gemini |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **instructions** | AIへのルール・規約 | ✅ | ✅ | ✅ | - | - | - |
| **skills** | 定型ワークフロー | ✅ | ✅ | ✅ | ✅ | ✅ | - |
| **agents** | 専用エージェント定義 | ✅ | ✅ | ✅ | ✅ | ✅ | - |
| **prompts** | スラッシュコマンド | ✅ | - | - | - | - | - |
| **commands** | スラッシュコマンド | - | ✅ | - | ✅ | - | - |
| **hooks** | ライフサイクルイベント処理 | ✅ | ✅ | ✅ | - | ✅ | - |

Codex、OpenCode、Gemini の `instructions` は、この表のように `apm install` で直接配置する対象ではなく、  
APM 公式ドキュメント上では、`apm compile` によって `AGENTS.md` や `GEMINI.md` のようなファイル形式へ変換によって提供されているようです。

### instructions ― AI へのルール・規約

コーディング規約や禁止事項など、AI に常に守らせたいルールを配布します。

`instructions` という名前は APM 側の分類名であり、各 AI ツール側で必ずこの名前の機能として提供されているわけではないためツール個別に読み替えが必要です。  
実際には、Claude なら rules、Copilot なら custom instructions、Cursor なら rules といった既存の仕組みに変換・配置されます。

インストールすると Claude なら `.claude/rules/`、Copilot なら `.github/instructions/` に配置されます。  
Claude であればこのディレクトリを自動で読み込みます。一方Copilot はファイルの frontmatter 設定によって読み込みの挙動が異なるようです。

<https://code.claude.com/docs/en/claude-directory#file-reference>  
<https://docs.github.com/ja/copilot/how-tos/configure-custom-instructions/add-repository-instructions#creating-custom-instructions>

```
.claude/rules/coding-standards.md が配置される
  ↓
Claude Code が自動で読み込む
  ↓
「型ヒントを付けて」と指示しなくても守られる
```

### skills ― 定型ワークフロー

「コードレビューして」「テスト書いて」のような繰り返し発生する作業の手順を配布します。

インストールすると Claude なら `.claude/skills/`、Copilot なら `.github/skills/` に配置されます。熟練者が「AI にこう頼むとうまくいく」と知っているワークフローをチーム全員が使えるようになります。

```
.claude/skills/code-review/SKILL.md が配置される
  ↓
「コードレビューして」と頼むと skill が発動
  ↓
チームで統一された観点でレビューが走る
```

割と有名な気がするので、詳細はツール個別に他に良い記事があると思うのでこの記事で深くは触れていきません。

### agents ― 専用エージェント定義

特定の役割に特化した AI ペルソナを配布します。

インストールすると Claude なら `.claude/agents/`、Copilot なら `.github/agents/` に配置されます。「セキュリティレビュー専任」「API 設計レビュー専任」のような役割特化エージェントをチーム全員が使えるようになります。

```
.claude/agents/security-reviewer.md が配置される
  ↓
エージェントを呼び出すと、セキュリティの観点に絞って動作する
  ↓
毎回プロンプトで役割を指示する必要がなくなる
```

割と有名な気がする（ry

### prompts / commands ― スラッシュコマンド

`/review`、`/security-check` のような呼び出し形式のワークフローを配布します。Copilot では prompts、Claude・OpenCode では commands という名前になっています。

インストールすると Claude なら `.claude/commands/`、Copilot なら `.github/prompts/` に配置されます。スラッシュコマンドを打つだけで定型の手順が走るため、チームの AI 活用を標準化しやすくなります。

```
.claude/commands/security-check.md が配置される
  ↓
/security-check と打つだけでセキュリティチェックが走る
```

割と有名な（ry

### hooks ― ライフサイクルイベント処理

AI がツールを実行する前後などのタイミングで自動で走らせる処理を配布します。

インストールすると各ツールの hooks 設定に統合されます。たとえば「ファイル変更後に自動でリントを走らせる」「危険なコマンドの実行前に確認を挟む」といった処理をチーム共通で適用できます。

```
hooks/post-edit.json が配置される
  ↓
ファイル編集のたびに自動でリントが走る
  ↓
AI が規約違反のコードを書いてもすぐ気づける
```

最近ハーネス流行ってますよね。割と（ry

### MCP サーバーの依存管理

MCP（Model Context Protocol）サーバーも `apm.yml` で宣言してバージョン付きで管理できるようです。  
便利ですねぇ。

**宣言方法**

`apm.yml` の `dependencies.mcp` に書きます。primitives の `dependencies.apm` とは別セクションです。

```
name: your-project
version: 1.0.0
dependencies:
  apm:
    - myorg/coding-standards       # primitives（ファイルコピー）
  mcp:
    - io.github.github/github-mcp-server   # MCP レジストリから取得
```

<https://microsoft.github.io/apm/reference/manifest-schema/>

**インストール後の挙動**

`apm install` を実行すると、検出された AI ツールの設定ファイルに MCP サーバーの接続情報が**エントリとして追加**されるとのこと。  
ファイル全体を置き換えるのではなく、既存の設定はそのまま残るらしいです。

同名のサーバーが既に設定されている場合はスキップされるため、手動で追加済みの設定が上書きされることはないらしいので個人の設定とも共存できそうです。  
<https://microsoft.github.io/apm/reference/cli-commands/#apm-install---install-dependencies-and-deploy-local-content>

## 個人的に便利そうだと思った話

**必要なものだけ対応みたいにできるらしい**：領域ごとにディレクトリを分け、必要なものだけ選んでインストールできるみたいです。  
<https://microsoft.github.io/apm/guides/skills/>

プロジェクトごとに取り込むものを取捨選択できると、  
渋りそうですよねぇ。

## 調べた所感

個人のものはもうこれでいいかなという気持ちでいます。

シンボリックリンクでもいいんですが、設定忘れがちだし  
端末跨いだ時にコピペで移植するのも億劫だったのでほんとにありがたいです。

チーム開発に持ち込めるかはこれからなので、  
少しずつでも布教していきたいとは思っています。

布教過程で面白そうな話ができればどこかで記事にしようと思います。

## 参考資料

<https://microsoft.github.io/apm/>  
<https://code.claude.com/docs/ja/overview>  
<https://developers.openai.com/codex>  
<https://docs.github.com/ja/copilot>
