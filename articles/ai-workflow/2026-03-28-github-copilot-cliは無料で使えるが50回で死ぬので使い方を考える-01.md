---
id: "2026-03-28-github-copilot-cliは無料で使えるが50回で死ぬので使い方を考える-01"
title: "GitHub Copilot CLIは無料で使えるが「50回で死ぬ」ので使い方を考える"
url: "https://zenn.dev/catatsumuri/articles/92a2145f15b7b4"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

<https://github.com/features/copilot/cli?locale=ja>

## TL;DR

## このエージェントについて

まず、このエージェントはユーザーアカウントがgithubに登録している限りではあるものの**珍しく無料で使うことができる**。ただしプレミアムリクエスト（エージェント問い合わせ）は`50`回しかないとされている。

![](https://static.zenn.studio/user-upload/c3b67fb57af7-20260328.png)  
*無料だと`50`回使える <https://github.com/features/copilot/plans?locale=ja> より*

この「プレミアムリクエスト」という概念が分かりづらいのだが、それは後ほど解説するとして、インストールをしないと始まらないので、まずはそこからやってみよう。

## インストールと起動

### インストール

一番シンプルなのは`curl`からの手動インストールだと思う。

```
# curl経由
curl -fsSL https://gh.io/copilot-install | bash
```

こんな感じでインストールできる。

```
$ curl -fsSL https://gh.io/copilot-install | bash
Installing GitHub Copilot CLI...
Downloading from: https://github.com/github/copilot-cli/releases/latest/download/copilot-linux-arm64.tar.gz
✓ Checksum validated
✓ GitHub Copilot CLI installed to /home/admin/.local/bin/copilot

Installation complete! Run 'copilot help' to get started.
```

### 起動

`copilot`で起動する

### ログインは必須

冒頭で書いた通り、githubにログインしないと使えないので`/login`する。

![](https://static.zenn.studio/user-upload/aa66e23ce1a2-20260328.png)  
*いつもの？アレ*

![](https://static.zenn.studio/user-upload/12fdc885736c-20260328.png)  
*`/limit`で確認*

## ある程度、情報を確認してみる

### モデルを確認する

`Claude 4.6`がデフォルトだが、GPT系もサポートするのがこのエージェントの特徴。

![](https://static.zenn.studio/user-upload/63019109fcc6-20260328.png)  
*モデル一覧*

### 簡単な質問に対してのLimitを見てみよう

たとえば

AIへのプロンプト

```
このリポジトリーにはupstreamが設定されていますか？
```

![](https://static.zenn.studio/user-upload/719870e5568f-20260328.png)  
*回答*

![](https://static.zenn.studio/user-upload/9b528b587cd8-20260328.png)  
*1発に対して1使用*

となっているのだが、以下のような軽い会話を乱発しても「プレミアム」リクエスト扱いにはなっていない感じがする。

![](https://static.zenn.studio/user-upload/85bcf3877165-20260328.png)  
*雑な会話でもどんどん消費されているように見える*

結局、カウント自体はヘヴィーな処理だけ行われているようで、これのusageに関してはgithubのダッシュボードで見るのが確実っぽい

<https://github.com/settings/billing/premium_requests_usage>

![](https://static.zenn.studio/user-upload/3b28979fb479-20260328.png)  
*意外と見た目ほどカウントされていないということもあるっぽい*

とるに足りない応答はプレミアムリクエストじゃなくてシンプルなリクエストに落ちてる可能性もありますね。

## いずれにせよgit系の仕事が強いように設定されている

### github-mcp-server がビルトインで組み込まれている

`/mcp`してみると分かるが、ビルトインでGitHub連携MCPが有効となっている

![](https://static.zenn.studio/user-upload/f8cc9c40034b-20260328.png)  
*`/mcp`した図*

mcpを使うとtokenガーみたいな話があるけど、基本的にカウントベースなのでそこは気にしなくていいのかも？

### ghコマンドを設定させる

このエージェントはどうやっても`GitHub`と連携した方が便利であるため、github連携するにおいては **`gh`コマンドは割と必須** である。入っていないなら入れた方がよい。

![](https://static.zenn.studio/user-upload/f0dac6e2831e-20260328.png)  
*`gh`コマンドを設定させる*

ここで途中**トークンの入力**があるので、事前に用意しておくこと

![](https://static.zenn.studio/user-upload/a87eba963079-20260328.png)  
*設定された*

## gitオペレーションあるいはgithub連携特化の使い方を考えてみる

フリーだと特に回数が少ないため、`git`のコマンドオペレーション、あるいは`GitHub`の連携オペレーションに特化する使い方がまず考えられる。

ここではgithub連携の例として弊リポジトリ <https://github.com/catatsumuri/react-starter-kit-ja>  
に関してupstreamの <https://github.com/laravel/react-starter-kit> をmergeさせてみよう。

### 重要なのは1つのコマンドに詰めこむことかも

まずこれをcloneした後、以下のようなプロンプトを与える

AIプロンプト

```
upstreamが設定されていなければfork元のupstreamをセットしmergeしてcommitして適切なPR作ってpushしてください
```

ここで通常cloneしただけではupstreamは設定されていないが、これはGitHubでforkしてあるので、その情報をエージェントが取得し、upstreamを自動的に設定してくれる

![](https://static.zenn.studio/user-upload/784ba0ff59e1-20260328.png)  
*GitHub同士ならforkも追いかけてupstreamが <https://github.com/laravel/react-starter-kit> に設定されている*

![](https://static.zenn.studio/user-upload/5649e8867264-20260328.png)  
*PRが設定された*

では見てみよう

![](https://static.zenn.studio/user-upload/1a52778db290-20260328.png)  
*<https://github.com/catatsumuri/react-starter-kit-ja/pull/2>*

![](https://static.zenn.studio/user-upload/467be3251310-20260328.png)  
*diffもある程度確認しておく*

最終的にwebからmergeしてもいいし、以下のようにしてもよい

AIへのプロンプト

```
PR:2をmainにmergeしてください
```

![](https://static.zenn.studio/user-upload/ad6248100198-20260328.png)  
*mergeされた*

### それ以外の使い方

基本的にはgithub連携しておくと話が早い感じで、たとえばすんごいでかいコミットをかなり複雑に見てもらった後に詳細にcommitメッセージを作らせるとかいう使い方はよいと思う。

issueを捌いたり、OSS運用なら知らない人がPRしてきた場合にそれを評価させたり、あるいは既存の動かない問題をissueとしてレポートさせたりなどがあるかも。もうちょいまともに使ってみないとあまり確信的なことは書けないが。

あとは、GitHubのCI/CDが落ちたときの解決などは、多分優秀に動作するはず。たぶん。

## 前提ファイル

これは**AGENTS.md**とか**CLAUDE.md**みたいなファイルではなく、githubらしく **.github/** 以下の **.github/copilot-instructions.md**に配置する。

たとえば

.github/copilot-instructions.md

```
# GitHub Copilot 指示

## 言語

全ての応答は日本語で行ってください

- **コミットメッセージ**はすべて**英語**で記述してください。
- **プルリクエストのタイトルと説明**はすべて**英語**で記述してください。
- コードコメントやドキュメントは、プロジェクトの既存の言語規則に従ってください。
```

みたいな

## ドキュメンター

AIへのプロンプト

```
プロジェクトの内容を徹底調査します、
docs/ ディレクトリ以下にこのアプリケーションの構造を解説した
markdownページを用意しドキュメントサイトを作る準備をしてください
```

この手の重ための処理はいいかも

![](https://static.zenn.studio/user-upload/83e7423d1f72-20260328.png)

作らせたドキュメントをgithub pagesでリリースさせるなど

<https://catatsumuri.github.io/react-starter-kit-ja/>

まあ公開する必要はないにせよ、重めの処理をcopilot cliで作らせておいて別のagentに評価させる、とかいう使い方も考えられる

## 次の一手

メインのエージェントからskillとか使ってサブ的に起動する方法も考えられるかもしれませんな
