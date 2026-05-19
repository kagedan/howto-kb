---
id: "2026-05-18-claude-code-context7で最新docsに強いai開発環境を作る-01"
title: "Claude Code + Context7で「最新docsに強いAI開発環境」を作る"
url: "https://zenn.dev/reina_codes/articles/context7claude"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "LLM"]
date_published: "2026-05-18"
date_collected: "2026-05-19"
summary_by: "auto-rss"
query: ""
---

最近、Claude Code をかなり使っています。  
便利なのですが、ひとつ気になっていたのが ドキュメントの精度 でした。

たとえば、

1. Next.js の情報が少し古い
2. React Canary の仕様がズレている
3. Tailwind CSS v4 の説明が怪しい
4. TanStack 系の breaking changes を取り逃す

そこで今回は、次の 3 つを組み合わせて、**docs 検索に強い Claude 環境**を作ってみました。

* Claude Code
* Context7 MCP
* `.claude/DocsExplorer.md`

Agent Framework のような重い仕組みは使っていません。設定はシンプルです。

## こんな感じで使える

Claude にプロンプトを投げると、おおよそ次の流れで動きます。

1. Context7から最新のdocsを取得
2. markdownベースの情報を優先
3. 公式 docsを優先
4. Claudeが整理して要約

実際に試したプロンプトは、後半の **[実際かなり便利だった例](#%E5%AE%9F%E9%9A%9B%E3%81%8B%E3%81%AA%E3%82%8A%E4%BE%BF%E5%88%A9%E3%81%A0%E3%81%A3%E3%81%9F%E4%BE%8B)** にまとめています。

## 前提

* macOS
* Claude Code 導入済み
* Node.js 導入済み

## 1. Context7 MCP を入れる

インストールはこれだけです。

```
npm install -g @upstash/context7-mcp
```

動作確認:

起動ログが出れば OK です。

## 2. Claude 側の MCP 設定

Claude 用の設定ファイルを作成します。

```
mkdir -p ~/.config/claude
touch ~/.config/claude/mcp.json
```

`mcp.json` の中身は次のとおりです。

```
{
  "mcpServers": {
    "context7": {
      "command": "context7-mcp"
    }
  }
}
```

かなりシンプルです。

## 3. docs 用の Prompt を作る

ここが今回のメインです。プロジェクト直下に `.claude/DocsExplorer.md` を作ります。

```
mkdir -p .claude
touch .claude/DocsExplorer.md
```

中身の例です。

```
# DocsExplorer

You are a documentation specialist that fetches up-to-date docs for libraries, frameworks, and technologies.

## Workflow

When given one or more technologies/libraries to look up:

1. Execute ALL lookups in parallel
2. Use Context7 MCP as primary source
3. Fall back to web search
4. Prefer:
   - llms.txt
   - markdown docs
   - raw docs

## Output Style

- concise
- practical
- code-first
- mention version compatibility
```

これだけでも、Claude の docs 検索の動き方がかなり変わります。

特に次の点がよかったです。

* まず Context7 を見にいく
* markdown を優先する
* 実装例ベースで返してくれる

## 4. CLAUDE.md で自動読み込み

さらに `.claude/CLAUDE.md` も追加します。

中身:

```
Read DocsExplorer.md before responding.

Use Context7 MCP whenever documentation lookup is needed.
```

これで、プロジェクト単位の Claude 設定として使えます。

## 最終的な構成

```
your-project/
├── .claude/
│   ├── CLAUDE.md
│   ├── DocsExplorer.md
│   └── workflows/
├── src/
└── package.json
```

Frontend プロジェクトとの相性もよかったです。

## 実際に試してみた結果：

設定が終わったあと、実際に Claude に投げてみてよかったプロンプトです。いずれも Context7 経由で最新 docs を参照したうえで答えてくれます。

### 1. 検証①：最新の Next.js App Router docs を取得する

まずはシンプルに、公式 docs を引いてもらうところから試しました。

```
Use Context7 to fetch the latest Next.js App Router docs.
```

以前は学習データベースの説明が混ざることがありましたが、Context7 経由だと **App Router 前提の最新情報**が返ってきやすくなりました。

### 2. 自分のコードを最新 Next.js docs と突き合わせる

Context7 が動いていることを確認できたら、次のプロンプトがおすすめです。手元のコードを最新 docs と照合して、直すべき点を一覧にしてもらえます。

```
Compare my code against the latest Next.js docs.
Identify:
- deprecated patterns
- cache issues
- server/client boundary mistakes
- outdated data fetching
- unnecessary client components
- opportunities to simplify

Wait for approval before applying changes.
Do NOT rewrite unless necessary.
```

実際に投げたところ、次のようなサマリーが返ってきました。

![コードレビュー結果のサマリー](https://i.gyazo.com/d778f28a744dfe67723d3bce45cb791c.png)

deprecated な書き方や cache の問題などが箇条書きになるので、**1 項目ずつ確認しながら直していく**のがやりやすかったです。いきなり書き換えてほしくないときは、`Wait for approval` と `Do NOT rewrite unless necessary` を入れておくのがポイントです。

### 2.検証②：better-auth の実装

通常の Claude Code だと、少し古い実装パターンを提案することがありました。  
一方で Context7 + DocsExplorer を使うと、最新 docs を参照しながら進められるので、実装のズレがかなり減ります

```
Add authentication using Google via better-auth.
use the docsexplorer agent to explore the relevant better-auth docs before implementing
```

のように指示すると、先に関連 docs を確認した上で実装を進めてくれます。  
特に、仕様変更が多いライブラリではかなり効果を感じました。

## Context7を使って良かったところ

### 1. めちゃ軽い

Agent Framework を入れなくても、次の 3 つだけでかなり実用的です。

* Claude Code
* MCP
* markdown ベースの prompt

設定もすぐ終わります。

### 2. docs の精度が上がる

特に、更新の速いライブラリで効きました。

* React
* Next.js
* Tailwind
* TanStack
* Vite

### 3. プロジェクトごとに役割を分けられる

`.claude/DocsExplorer.md` を差し替えるだけで、次のように切り替えられます。

* frontend 特化
* backend 特化
* infra 特化

地味に便利です。

## ハマったところ

### 1. `context7-mcp: command not found`

原因は npm の global path でした。

確認:

必要なら `~/.zshrc` に追加します。

```
export PATH="$PATH:$(npm bin -g)"
```

### 2. Documentation not found

Context7 を使い始めたとき、いちばんハマったのがこのエラーです。

```
Documentation not found or not finalized for this library.
```

`context7:get-library-docs` を実行したときに出やすく、React でも `/reactjs/react.dev` を指定して取れないことがありました。

#### 原因

最初は remote MCP 構成にしていました。

```
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

この構成だと、次のような事象がよく出ました。

* 一部のライブラリが取得できない
* `Documentation not found`
* `Failed to retrieve library documentation data`

#### 解決方法

ローカルで `npx` 実行に切り替えたら改善しました。さらに `@latest` と `--experimental-fetch` も追加しています。

最終的には、次の設定で安定しました。

```
{
  "mcpServers": {
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "--node-options=--experimental-fetch",
        "@upstash/context7-mcp@latest"
      ],
      "env": {}
    }
  }
}
```

これで React docs、mise docs、Next.js docs なども取得できるようになりました。

### 3. `resolve-library-id` を先に呼ぶ

Context7 では、`get-library-docs` の前に `resolve-library-id` を実行する必要があります。

```
ライブラリ名
  ↓
resolve-library-id
  ↓
Context7 用の library ID を取得
  ↓
get-library-docs
```

この順番を飛ばすと、失敗しやすいです。

#### 例: mise

最初は `Documentation not found` でしたが、`@latest` に変更したあとは `/jdx/mise` の docs も取得できるようになり、かなり改善しました。

## Claude 側で確認する方法

登録状況の確認:

ログの確認:

トラブル時にかなり助かりました。

## 参考

今回参考にした記事・ドキュメントです。

## まとめ

今回やってみて、「大きな Agent システムを組む」よりも、次の 3 つだけの方が実運用では扱いやすいと感じました。

* MCP
* 小さな Prompt 設計
* リポジトリ内の local config

Frontend 開発では最新 docs への追従が重要なので、Context7 との組み合わせはかなりおすすめです。まずは例 1 の docs 取得から試して、慣れたら例 2 のコード突き合わせまで試してみてください。
