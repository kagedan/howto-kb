---
id: "2026-04-02-claude-aiを使ってaws-ec2インスタンスを作成するcloudformationテンプレー-01"
title: "Claude AIを使ってAWS EC2インスタンスを作成するCloudformationテンプレートを作ってみた"
url: "https://qiita.com/new1low/items/dfb99a60f1b999a7c316"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## はじめに
今回コード生成AIを試しに使ってみようということでClaudeを使って、簡単なAWS EC2インスタンスを作成するためのテンプレートファイルを作ってみようと思います。

Claudeはどうやら、draw.ioのファイル（.drawio または .xml）をアップロードすると、そこからテンプレート作成までもっていってくれるそうなので、それも体験してみます。

### アップロードに使ったdraw.io
※qiitaに.drawio または .xml形式のファイルは添付できなかったので、画像を添付

- ![{C9FBE56E-D951-4BFA-939D-DB7B7F613E5C}.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4185984/f0b3988a-4598-4188-8758-7905ce1f331b.png)

## コード生成

アップロードの際に少し補足文書もいれてみた。
![{013E2F2A-CE4B-476E-95B4-A95EB20D85C7}.png](h
