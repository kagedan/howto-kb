---
id: "2026-04-16-cadソフトの操作を自然言語指示でaiに任せる-kiro-で-step-生成から-freecad-編-01"
title: "CADソフトの操作を自然言語指示でAIに任せる — Kiro で STEP 生成から FreeCAD 編集まで"
url: "https://zenn.dev/aws_japan/articles/45fb5d3130035d"
source: "zenn"
category: "ai-workflow"
tags: ["Python", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

はじめに
前回の記事では、AWS の「Auto&amp;Manufacturing - Kiro for Business Users」ワークショップを紹介しました。AI コーディングアシスタント「Kiro」を使い、自然言語の指示だけで CFD シミュレーションや 3D モデリングを行う内容です。
前回の記事の「応用：より複雑な産業機械の3Dモデリング」セクションでは、6軸多関節ロボットアームの3Dモデルを自然言語の指示だけで生成しました。
このとき使ったのは Python の numpy-stl ライブラリで、三角形の頂点座標を直接計算して STL ファイルを出力する方法です。CA...
