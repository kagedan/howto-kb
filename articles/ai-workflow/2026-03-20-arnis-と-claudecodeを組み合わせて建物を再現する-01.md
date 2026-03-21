---
id: "2026-03-20-arnis-と-claudecodeを組み合わせて建物を再現する-01"
title: "Arnis と ClaudeCodeを組み合わせて建物を再現する"
url: "https://zenn.dev/musoukun/articles/e4673a57bb02f5"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-20"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

TL;DR
地図データから街を自動生成するツールのArnisが話題なので、これを使って街を再現しようとしてみました。
この記事では、イオンモール堺北花田を題材にして、たたき台の生成からリアルな外観への書き換えまでを書きます。
※思ってるより地道な作業が必要なので、ﾄﾞｶﾝと書き換わらないことはご了承ください。
※クオリティも完ぺきではないし、実験的なものとして見てください
※書いてないことで必要なものもあるかもしれないけど考え方だけ

 やりたいこと
現実の街を、Minecraftの中にそれっぽく再現する。
写真を1ピクセルずつコピーするのではなく、「この建物は白い壁で、ここがガラス...
