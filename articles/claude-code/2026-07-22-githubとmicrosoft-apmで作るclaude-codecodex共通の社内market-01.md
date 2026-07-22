---
id: "2026-07-22-githubとmicrosoft-apmで作るclaude-codecodex共通の社内market-01"
title: "GitHubとMicrosoft APMで作る、Claude Code・Codex共通の社内Marketplace"
url: "https://zenn.dev/inventit/articles/apm-marketplace"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude CodeやCodexを社内で利用していると、コーディング規約やレビュー手順を記述したSkill、社内データを参照するMCPサーバー、それらを組み合わせたプラグインが増えていきます。

これらを各開発者が手作業でコピーすると、Claude Code用とCodex用で導入方法が分かれ、更新やバージョン管理も難しくなります。

本記事では、MicrosoftのAgent Package Manager（APM）を利用し、GitHub上に社内Marketplaceを構築します。利用者はMarketplaceからパッケージをインストールするだけで、同じSkillとMCPサーバーをClaude CodeとCodexの両方から利用できるようにします。

# 今回作るもの

GitHubの[mtakahashi-ivi/apm-marketplace](https://github.com/mtakahashi-ivi/apm-marketplace)に、次のような社内Marketplaceを作成します。

```
apm-marketplace/
├── apm.yml
└── plugins/
    ├── prejudice-skill/
    └── prejudice-mcp/
```

Marketplaceには、次の2つのプラグインを登録します。

## Skillのみを含むプラグイン

LLMに「mtakahashiの偏見を考慮して回答する」という手順を与えるSkillです。

## SkillとMCPサーバーを含むプラグイン

Skillに加えて、`mtakahashi_prejudice`というローカルstdio MCPサーバーを利用します。

このMCPサーバーは`get_prejudice`ツールを公開し、指定したキーワードに対応する外部知識を返します。MCPサーバー自体の実装は、[「Vim一択」をLLMに教える：mtakahashiの偏見MCPサーバから外部知識を取得する](https://zenn.dev/inventit/articles/mtakahashi-prejudice-mcp-local)で扱っています。

本記事ではMCPサーバーの実装ではなく、APM Marketplaceへの組み込みと配布を中心に説明します。

# Marketplaceの用語と対応関係

ここでいう「Marketplace」は、パッケージの一覧を管理するAPMのMarketplaceです。Claude Code MarketplaceとAPM Marketplaceが別々に存在し、それぞれへ同じプラグインを登録するわけではありません。

APMでは、リポジトリの`apm.yml`にある`marketplace:`ブロックが原本です。`apm pack`を実行すると、その定義からClaude Codeが読む`.claude-plugin/marketplace.json`と、Codex向けの`.agents/plugins/marketplace.json`を生成できます。つまり、Claude Code MarketplaceはAPM Marketplaceの定義から生成されるClaude Code互換の成果物であり、Codex向け成果物も同じ定義から作られます。

| 用語 | この記事での意味 |
| --- | --- |
| APM Marketplace | `apm.yml`の`marketplace:`に定義する、パッケージのカタログ |
| Claude Code Marketplace | APM Marketplaceから生成される`.claude-plugin/marketplace.json` |
| Codex向けMarketplace | APM Marketplaceから生成される`.agents/plugins/marketplace.json` |
| パッケージ | APMが取得・依存解決・対象ハーネス向けに展開する配布単位。Claude Codeでいうプラグインに相当する |
| Skill / MCPサーバー | パッケージに含めて配布する機能 |

この関係を図にすると、次のようになります。

```
APM Marketplace
          |
          v
         APM
          |
    +-----+-----+
    |           |
Claude Code   Codex
```

# 全体構成

今回の構成は次のとおりです。

```
GitHub
└── apm-marketplace
    ├── Marketplace定義
    ├── Skill
    └── MCPサーバー
            |
            v
        apm install
            |
      +-----+-----+
      |           |
 Claude Code    Codex
```

Marketplace、Skill、MCPサーバーは、すべて一つのGitHubリポジトリに配置します。

# APMをHomebrewでインストールする

macOSでは、MicrosoftのHomebrew tapからAPMをインストールできます。

```
brew tap microsoft/apm
brew install apm
```

詳細は[Microsoftのhomebrew-apmリポジトリ](https://github.com/microsoft/homebrew-apm)を参照してください。

インストール後、コマンドが実行できることを確認します。

Homebrew自体が未導入の場合は、先に[Homebrew公式サイト](https://brew.sh/)の手順で導入してください。

# 事前準備

必要なものは次のとおりです。

* Gitリポジトリ（今回はGitHubを使用）
* GitリポジトリへアクセスできるGit認証
* APM
* Claude Code
* Codex
* Node.js
* mise

APMはGitを使用してMarketplaceを取得するため、最初に対象のGitリポジトリへ通常の`git clone`が成功することを確認します。今回はGitHubのSSH URLを例にしますが、Bitbucketなど別のGitホスティングでも、利用するGit URLと認証方法を置き換えれば同じです。

```
git clone git@github.com:mtakahashi-ivi/apm-marketplace.git
```

GitHub Enterprise Serverなどを使用している場合も、環境に応じたSSH URLを利用します。APMがパッケージを取得するときも、GitHubへのアクセスは通常のGitのSSH認証に任せます。

# Marketplaceリポジトリを作る

## リポジトリ構成

今回使用する構成は次のようにします。

```
apm-marketplace/
├── apm.yml
├── .claude-plugin/
│   └── marketplace.json
├── .agents/
│   └── plugins/
│       └── marketplace.json
└── plugins/
    ├── prejudice-skill/
    │   ├── apm.yml
    │   └── .apm/
    │       └── skills/
    │           └── mtakahashi-prejudice/
    │               └── SKILL.md
    └── prejudice-mcp/
        ├── apm.yml
        ├── .apm/
        │   └── skills/
        │       └── mtakahashi-prejudice/
        │           └── SKILL.md
        ├── src/index.ts
        ├── package.json
        ├── package-lock.json
        ├── tsconfig.json
        └── mise.toml
```

## Skillのみのプラグインを作る

Skillには、例えば次のような処理を定義します。

* ユーザーの質問から対象の技術要素を抽出する
* mtakahashiの価値観を考慮して回答する
* 一般的な説明と偏見を区別して出力する

配置場所は次のとおりです。

```
plugins/prejudice-skill/
├── apm.yml
└── .apm/
    └── skills/
        └── mtakahashi-prejudice/
            └── SKILL.md
```

`SKILL.md`には、Skillを呼び出す条件と実行手順を記述します。

```
---
name: mtakahashi-prejudice
description: mtakahashiの技術的な偏見を考慮して回答する
---

ユーザーから技術選定や開発ツールについて質問された場合、
一般的な回答に加えて、mtakahashiの偏見を明確に区別して回答する。
```

## MCPサーバーを含むプラグインを作る

SkillはLLMの判断手順を提供し、MCPサーバーは会話の外部にあるデータを提供します。

```
Skill
  └── いつ偏見を取得し、回答へどう反映するかを定義する

MCPサーバー
  └── 実際の偏見データを返す
```

MCPサーバーを含むプラグインは次の構成にします。

```
plugins/prejudice-mcp/
├── apm.yml
├── .apm/skills/mtakahashi-prejudice/SKILL.md
├── src/index.ts
├── package.json
├── package-lock.json
├── tsconfig.json
└── mise.toml
```

`mise.toml`では、Node.jsのバージョンとMCPサーバーの起動タスクを定義しています。

```
[tools]
node = "22.14.0"

[tasks.build]
run = "npm run build"
depends = ["install"]

[tasks.install]
run = "npm ci"

[tasks.start]
run = "npm start"
depends = ["build"]
```

単体で検証する場合は、次のコマンドを実行します。

```
cd plugins/prejudice-mcp
mise install
mise run build
mise run start
```

APMのマニフェストでは、MCPサーバーを次のように定義します。

```
name: prejudice-mcp
version: 1.0.0
description: mtakahashi の偏見を Skill とローカル MCP サーバーから提供するプラグイン
targets:
  - claude
  - codex
  - agent-skills

dependencies:
  mcp:
    - name: mtakahashi_prejudice
      registry: false
      transport: stdio
      command: mise
      args:
        - -C
        - ./apm_modules/mtakahashi-ivi/apm-marketplace/plugins/prejudice-mcp
        - run
        - start
      cwd: ./apm_modules/mtakahashi-ivi/apm-marketplace/plugins/prejudice-mcp
```

`cwd`と`mise`の`-C`で、インストール先の`apm_modules`配下にあるプラグインのディレクトリを作業ディレクトリとしてMCPサーバーを起動します。

# Marketplaceを定義する

リポジトリルートの`apm.yml`に、Marketplaceと掲載するプラグインを定義します。

```
name: apm-marketplace
version: 1.0.0
description: Internal AI agent plugins for Claude Code and Codex
targets:
  - claude
  - codex
  - agent-skills

marketplace:
  name: apm-marketplace
  owner:
    name: inventit
  packages:
    - name: prejudice-skill
      version: 1.0.0
      description: mtakahashi の技術的な偏見を Skill だけで提供するプラグイン
      source: plugins/prejudice-skill
    - name: prejudice-mcp
      version: 1.0.0
      description: mtakahashi の偏見を Skill と MCP サーバーから提供するプラグイン
      source: plugins/prejudice-mcp
```

Marketplaceには、Skillのみのパッケージと、SkillとMCPサーバーを含むパッケージの両方を掲載します。

## 空のMarketplaceにパッケージを追加する

Marketplaceリポジトリを空の状態から作る場合は、まずリポジトリのルートでAPMのMarketplace定義を初期化します。

```
apm init
apm marketplace init --name apm-marketplace --owner inventit
```

`apm marketplace init`によって、`apm.yml`に`marketplace:`ブロックが追加されます。同じモノレポ内のディレクトリをパッケージとして登録する場合は、GitHub URLやSSH URLではなく、`apm.yml`の`packages`へローカルパスを記述します。

```
marketplace:
  name: apm-marketplace
  owner:
    name: inventit
  packages:
    - name: prejudice-skill
      version: 1.0.0
      description: mtakahashi の技術的な偏見を Skill だけで提供するプラグイン
      source: plugins/prejudice-skill
    - name: prejudice-mcp
      version: 1.0.0
      description: mtakahashi の偏見を Skill と MCP サーバーから提供するプラグイン
      source: plugins/prejudice-mcp
```

`source`は`apm.yml`から見た相対パスです。ここで追加しているのはMarketplaceの掲載情報です。

追加したら、生成物を確認してからGitへコミットします。

```
apm marketplace check --offline
apm pack
git add apm.yml .claude-plugin/marketplace.json .agents/plugins/marketplace.json
git commit -m "Add prejudice packages to marketplace"
```

# Marketplaceを検証・パッケージ化する

まず、Marketplaceの定義を検証します。

```
apm marketplace check --offline
```

必要に応じてMarketplaceをパッケージ化します。

生成されるファイルは、概ね次のようになります。

```
.claude-plugin/marketplace.json
.agents/plugins/marketplace.json
```

`apm.yml`を編集元とし、生成されたJSONファイルはAPMから生成される成果物として扱います。

検証後、MarketplaceリポジトリをGitHubへpushします。

```
git add .
git commit -m "Add internal APM marketplace"
git push origin main
```

# 利用者のAPM Marketplace利用方法

## GitHubの接続確認

利用者の端末からMarketplaceリポジトリを取得できることを確認します。

```
git clone git@github.com:mtakahashi-ivi/apm-marketplace.git
```

APM独自の認証を設定するのではなく、通常のGit認証を使用します。

## MarketplaceをAPMへ追加する

GitHub上の[Marketplaceリポジトリ](https://github.com/mtakahashi-ivi/apm-marketplace)を、APMの利用可能なMarketplaceとして追加します。

```
apm marketplace add git@github.com:mtakahashi-ivi/apm-marketplace.git --name mycompany --ref v1.0.0
```

登録済みのMarketplaceを確認します。

Marketplace内のパッケージを検索します。

```
apm search prejudice@mycompany
```

## パッケージをインストールする

APMでインストールする単位は「パッケージ」です。Claude Codeではパッケージがプラグインとして展開されますが、`apm install prejudice-mcp@mycompany`が取得しているのは`prejudice-mcp`という名前のAPMパッケージです。

```
apm install prejudice-mcp@mycompany
```

このパッケージでは、Skill、`mtakahashi_prejudice` MCPサーバー、MCPサーバーの起動設定がインストールされます。

## プロジェクトの依存関係として管理する

利用するパッケージは、対象プロジェクトの`apm.yml`に記録できます。

```
name: example-project
version: 1.0.0

targets:
  - claude
  - codex
  - agent-skills

dependencies:
  apm:
    - prejudice-mcp@mycompany
```

以降は、プロジェクト上で次のコマンドを実行すれば、必要なパッケージを再現できます。

Marketplaceは登録時に指定したタグを参照するため、パッケージを更新した場合は新しいタグを作成してMarketplaceを登録し直します。

```
apm marketplace update mycompany
apm install
```

# Claude Codeから利用する

APMによるインストール後、対象プロジェクトでClaude Codeを起動します。

Claude Codeのセッション内では、`/mcp`でも確認できます。

次のような質問を実行し、`get_prejudice`ツールが呼び出されることを確認します。

```
エディタを選ぶ時の一般的な判断基準を説明してください。
そのうえで、mtakahashiの偏見もMCPサーバーから取得してください。
```

# Codexから利用する

同じプロジェクトでCodexを起動し、MCPサーバーの登録状態を確認します。

CodexのTUIでは、`/mcp`でも確認できます。Claude Codeと同じ質問を実行し、同じSkillとMCPサーバーをCodexからも利用できることを確認します。

# APMを使わずに直接設定する場合との比較

少数のプロジェクトへMCP設定を追加するだけなら、Claude Codeの`.mcp.json`やCodexの`.codex/config.toml`を手作業で管理しても問題ありません。

一方、社内で複数のSkillやMCPサーバーを配布する場合は、Claude Code用設定、Codex用設定、Skillファイル、MCPサーバー本体、バージョン、更新手順をそれぞれ管理する必要があります。

APMを利用すると、これらを一つのパッケージとMarketplaceにまとめられます。

# まとめ

今回構築した仕組みは次のとおりです。

```
GitHub
└── 社内Marketplace
    ├── Skillのみのプラグイン
    └── Skill + MCPサーバーのプラグイン
            |
            v
           APM
            |
      +-----+-----+
      |           |
 Claude Code    Codex
```

GitHubはMarketplaceとプラグインの保管場所として使用し、APMはMarketplaceからプラグインを取得してClaude CodeとCodex向けの形式へ展開します。

Claude CodeとCodexを併用する環境では、ハーネスごとにSkillやMCP設定を手作業で管理するのではなく、GitHub上のAPM Marketplaceを共通の配布元として利用できます。

同じ仕組みは、社内コーディング規約の参照、JiraやConfluenceの検索、AWS環境の調査、障害対応手順の提供、Terraformレビューなどへ発展させられます。

参考:
