---
id: "2026-04-03-cesium-for-unity-東京3dマップで鬼ごっこゲームを作ったmixamoキャラレーダーu-01"
title: "Cesium for Unity × 東京3Dマップで鬼ごっこゲームを作った【Mixamoキャラ・レーダーUI追加】"
url: "https://zenn.dev/acropapa330/articles/tokyo_tag_game_cesium"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

Cesium for Unity × 東京3Dマップで鬼ごっこゲームを作った【地面落下バグとの戦い】

 はじめに
「現実の東京を舞台にした鬼ごっこゲームが作りたい」という思いつきから、Cesium for Unity を使ってリアルな東京の3D建物マップでプレイできる鬼ごっこゲームを作りました。
完成してみたら鬼に本当に捕まったので、ゲームとして成立していました笑
ただし、Cesium を使ったゲーム開発には独特のハマりポイントがありました。特に 「プレイヤーが地面を突き抜けて Y=-451 まで落下する」 問題には相当悩まされました。この記事ではその解決策を中心に記録します。

...
