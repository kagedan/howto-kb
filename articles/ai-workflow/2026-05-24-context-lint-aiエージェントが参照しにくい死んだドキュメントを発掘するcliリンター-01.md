---
id: "2026-05-24-context-lint-aiエージェントが参照しにくい死んだドキュメントを発掘するcliリンター-01"
title: "context-lint — AIエージェントが参照しにくい「死んだドキュメント」を発掘するCLIリンター"
url: "https://zenn.dev/aki__0421/articles/ca1fe841506933"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "OpenAI", "zenn"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

AIエージェントにコードを書いてもらう機会が増えるほど、「どの情報をエージェントに見せるか」が大事になってきます。

最近、OpenAIのこちらの記事を読みました。

<https://openai.com/ja-JP/index/harness-engineering/>

この記事では、Codexを使って、手書きコードなしでソフトウェアを作る実験が紹介されています。印象的だったのは、エンジニアの役割が「コードを書くこと」から、「エージェントがうまく動ける環境を整えること」へ移っている点です。

その中でも特に刺さったのが、`AGENTS.md` を分厚いマニュアルにしない、という話でした。

## AGENTS.md はマニュアルではなく、地図にする

OpenAIの記事では、巨大な `AGENTS.md` にすべてを書こうとすると、うまくいかないと説明されています。

理由はとても自然です。

* コンテキストは限られている
* すべてを重要だと書くと、何が本当に重要なのかわからなくなる
* 長いマニュアルはすぐ古くなる
* 大きな1ファイルは機械的に検証しづらい

そこで、`AGENTS.md` は百科事典ではなく「目次」として扱います。

短い `AGENTS.md` から、`docs/` 配下の設計ドキュメント、実行計画、仕様、品質や信頼性のドキュメントへ案内する。必要な情報はリポジトリ内に置き、エージェントが辿れるようにしておく。

これは、人間向けのドキュメント整理というより、AIエージェント向けのナレッジ設計に近いと感じました。

## 見つけられないドキュメントは、ほとんど存在しない

AIエージェントは、人間のように「たぶんこの辺にあるはず」と空気を読んで探してくれるわけではありません。

入口として渡されたファイルがあり、そこから辿れるリンクがあり、リポジトリ内に実際のファイルがある。そこまで整って、ようやくコンテキストとして使えます。

逆に言うと、次のようなドキュメントは、エージェントにとってはかなり危ういです。

* `docs/architecture.md` はあるが、`AGENTS.md` から辿れない
* Markdownリンクが古く、存在しないファイルを指している
* 本文やコードブロック内のファイルパスが壊れている
* 重要な設計メモがあるのに、CIで一度も検証されていない

こうした「あるけれど、参照されにくいドキュメント」は、少しずつ死んでいきます。

そこで作ったのが [`context-lint`](https://github.com/aki-0421/context-lint) です。

## context-lint とは

`context-lint` は、AIエージェント向けのリポジトリドキュメントを、辿れる状態に保つためのCLIリンターです。

たとえば `AGENTS.md` を入口にして、ローカルMarkdownリンクや、本文中のファイルパスらしき文字列を辿ります。そして、次のような問題を検出します。

* entryファイルが存在しない
* ローカルMarkdownリンクの参照先が存在しない
* 本文やコードブロック内のファイルパスが壊れている
* `requiredReachable` に指定した重要ドキュメントが入口から辿れない

やりたいことはシンプルです。

`AGENTS.md` を小さな地図にしつつ、そこから必要なドキュメントへちゃんと到達できる状態を保つことです。

## 使い方

インストールします。

```
go install github.com/aki-0421/context-lint/cmd/context-lint@latest
```

プロジェクトルートに `.context-lint.yaml` を置きます。

```
linter:
  document:
    entry: AGENTS.md
    requiredReachable:
      - docs
    excludes:
      - README.md
```

実行します。

デフォルトでは、ドキュメント上の指摘は warning として扱われ、終了コードは `0` です。

エラーで落としたい場合は `--strict` フラグを利用可能です。

## GitHub Actionsで使う

GitHub Actionsでも使えます。

```
jobs:
  context-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aki-0421/context-lint@v1
        with:
          strict: true
```

## まとめ

OpenAIの記事を読んで、AIエージェント時代のドキュメントは、単に「書いてある」だけでは足りないと感じました。

大事なのは、入口があり、リンクがあり、必要な情報に辿れることです。

`context-lint` は、そのための小さなCLIです。

`AGENTS.md` を地図として使い、リポジトリ内のドキュメントをAIエージェントが辿れる状態に保ちたい方は、ぜひ試してみてください。

<https://github.com/aki-0421/context-lint>
