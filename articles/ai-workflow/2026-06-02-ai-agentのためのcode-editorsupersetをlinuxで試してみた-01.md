---
id: "2026-06-02-ai-agentのためのcode-editorsupersetをlinuxで試してみた-01"
title: "AI agentのためのCode Editor、SupersetをLinuxで試してみた"
url: "https://zenn.dev/kay1974/articles/60a0fdb67b5356"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "VSCode", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIエージェントのオーケストレーションツールを調べていたところ  
<https://zenn.dev/imnoaz/articles/03dc1176767572>  
の記事を読み、どんなものなのか、試してみました。

最初Githubで検索したら、BIツールの方のSupersetに行ってしまい、  
<https://github.com/apache/superset>

AI agentのためのCode Editorはこっちでした。  
<https://superset.sh/>  
<https://github.com/superset-sh/superset>  
むむっ、Mac専用なのか？  
GitHubのリポジトリに「Download for MacOS」しかないので、またMac壁にあたったのかと思いましたが、No test状態ではあるものの、Linuxでも使えるようだったので、リポジトリをクローンしてみました。  
Development.mdをみると、

> Prereqs: bun, docker, jq, caddy

とのことだったので、bun, caddyを導入した状態で、（jqは入っていた）dockerの代わりにpodman（alias docker=podman）で出来るか試してみました。  
インストールスクリプトは`./.superset/setup.local.sh`  
実施してみると、エラーになる。調べてみるとPostgresDBのインストールに失敗していたので、別途PostgresDBをインストール。ArchLinuxのnpmのバージョンが高すぎるのか、バージョンを落として、あと、ちょこちょこスクリプトにパッチ当てて実行したら、アプリがセットアップできました。  
この辺はバージョンが上がってくると治ってくるのかな。

## 起動させてみる

起動させてみると、なかなかUIが出てこない。

* Postgres
* Neon Proxy
* Electric sync
* Caddy
* api
* desktop renderer

サービスがいっぱい並走してるからですね。  
なぜこんなにサービスが必要なのか、考えてみましたが、  
「複数のAIエージェントの状態をリアルタイムで状態共有したいから」「ブラウザdiff UIのため」なのかな。「マルチユーザでさわるから」も少しあるかもしれない。

起動して、さわってみると、Gitリポジトリをつくらないと、AI Agentを起動させられない感じです。環境分離をGit worktreeに依存していることがよくわかる作りとも言えます。

> 余談ですがGit worktreeは分離させるのは簡単ですが、マージコミットしくじると、結構手間かかるので注意ですよ。

AI Agentが作ったものをdiff差分確認とかはお手軽にできますね。これは良い点。また、エージェント起動も割と簡単に行えるようになっています。

## 感想

感想としては、メモリ／ＣＰＵが潤沢なら使ってもいいかも。くらいのレベル感ですね。私の環境では、ちょっと普段使いには採用できない感じ。

> まあ、VSCodeで重いといっているぐらいですからね。あしからず。
