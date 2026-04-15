---
id: "2026-04-14-openclawをraspberry-piで動かす手順claudeopenaiの切替付き-01"
title: "OpenClawをRaspberry Piで動かす手順（Claude→OpenAIの切替付き）"
url: "https://qiita.com/tatsuya1970/items/13d34ae0d00fd640361e"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

# はじめに

話題のOpenClawですが、
自分のPCをセキュリティリスクにさらしたくなく、
これまで導入を躊躇していました。

そこで、Raspberry Piのような独立したデバイス上でOpenClawを動かすことにしました。
これなら、万が一何かあってもリスクは最小限に抑えられます。


# 使用機器
Raspbery pi 5

![IMG_2889.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/291592/8c257660-7b58-4567-8273-e6c258e83783.jpeg)



# Raspberry Piの設定

こちらの記事を参考に設定しました。
https://raspi-school.com/getting-started-with-raspberrypi/



# OpenClaw のインストール

ラズパイのターミナルで以下実行

```
$ curl -fsSL https://openclaw.ai/install.sh | bash
```

インス
