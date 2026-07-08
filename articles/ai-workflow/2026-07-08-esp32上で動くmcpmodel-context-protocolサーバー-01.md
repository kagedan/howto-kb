---
id: "2026-07-08-esp32上で動くmcpmodel-context-protocolサーバー-01"
title: "ESP32上で動くMCP(Model Context Protocol)サーバー"
url: "https://qiita.com/nishioka_sst/items/1db9ee2da7eb6e14c828"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "Python", "qiita"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

LUNAとは  
LUNAは、ESP32上で動くMCP(Model Context Protocol)サーバーです。Claude AIなどのAIアシスタントとMCP経由で接続することで、天体望遠鏡の自動制御（LX200互換・WiFi化）をはじめとした組み込み開発を、AIとの会話だけで進められるようにすることを目指しています。  
<https://github.com/OnStepNinja/LUNA>

開発の目的  
従来、ESP32のファームウェア開発にはArduino IDEやPlatformIOでのコーディング、ビルド、書き込みといった手順が必要でした。LUNAはこの流れを大きく変え、「望遠鏡をLX200互換にしたい」「WiFi経由でGoToしたい」といった要望をAIに話しかけるだけで、Lua/MicroPythonスクリプトが生成・実機に反映される開発体験を提供します。

新しい開発プラットフォームとして  
LUNAが目指しているのは、コードを書く代わりにAIと対話しながらプログラムを作り上げていく「ノーコード×AI開発」のプラットフォームです。プログラミング未経験の天文愛好家でも、AIとのやり取りの中で望遠鏡制御システムを自分の手で作り上げられる——そんな新しい開発体験を、天体望遠鏡の自動制御という具体的なユースケースを通じて実現していきます。
