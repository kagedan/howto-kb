---
id: "2026-04-10-tailscaleでhttps通信local-pcのwebアプリにiphoneからアクセスする-01"
title: "Tailscaleでhttps通信。local PCのWebアプリにiphoneからアクセスする。"
url: "https://zenn.dev/nishina__n/articles/8a9a201b8f629e"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

Tailscale
Tailscaleを使うとスマホとlocalPCをセキュアかつ、無料で接続できる。しかもhttpsで接続することが可能になる。Webブラウザベースのアプリではhttpsで接続していなければマイクの利用などがブラウザ側で制限されるため、必須の設定である。
今回自作しているAIエージェントのVoxclawを接続したが、https接続する時に少し手間がかかったので、記載しておく。今回の方法はlocalPCでlocalhostのwebページを立ち上げる場合に有効なので、応用も効くと思う。

 Voxclaw
Voxclawは音声から意図推定して動作可能な軽量セキュアなAI...
