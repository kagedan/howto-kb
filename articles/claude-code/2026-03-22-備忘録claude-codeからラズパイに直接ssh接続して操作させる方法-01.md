---
id: "2026-03-22-備忘録claude-codeからラズパイに直接ssh接続して操作させる方法-01"
title: "【備忘録】Claude Codeからラズパイに直接SSH接続して操作させる方法"
url: "https://qiita.com/sk283/items/750d9ef502172cbbb5af"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに
 
ラズパイの自宅サーバー構築をClaude（Webチャット版）と進めていたのですが、毎回「このコマンドを実行して」→「結果はこうでした」のやり取りが発生して、正直しんどかったです。
 
そこで**Claude Code**（ターミナル版のClaude）を導入し、SSHでラズパイに直接接続させることで、コマンド実行からエラー対応まで全部自動でやってもらえるようになりました。
 
この記事では、Claude CodeからラズパイにパスワードなしでSSH接続できるようにするまでの手順をまとめます。
 
## 前提環境
 
| 項目 | 内容 |
|------|------|
| 操作PC | Claude Codeが動いているマシン |
| ラズパイ | Raspberry Pi 3（Raspberry Pi OS / Debian bookworm） |
| ネットワーク | 同一LAN内（PCとラズパイが同じネットワークにいる） |
 
:::note info
IPアドレスやユーザー名は環境に合わせて読み替えてください。この記事では以下を例として使います。
- ラズ
