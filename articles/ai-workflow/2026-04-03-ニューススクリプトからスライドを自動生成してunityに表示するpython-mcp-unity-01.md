---
id: "2026-04-03-ニューススクリプトからスライドを自動生成してunityに表示するpython-mcp-unity-01"
title: "ニューススクリプトからスライドを自動生成してUnityに表示する【Python + MCP + Unity】"
url: "https://zenn.dev/acropapa330/articles/yabou01_slide_mcp_unity"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "Python", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

はじめに
AIニュース動画自動生成パイプライン yabou01 の品質改善として、クロエちゃん（VRMアバター）の横に ニューススライドをリアルタイムで表示する機能 を実装しました。
実装したこと：

ニューススクリプト（Markdown）を解析してスライドPNGを自動生成（Pillow）
各ニュース記事のOG画像をスクレイピングしてスライドに埋め込む
UnityにC#スクリプトを仕込み、MCP経由でPythonからスライドを切り替える
録画中、音声の長さに合わせてスライドを自動切り替え

完成イメージ：
録画中
  ↓ TTS音声1件分の尺が終わると
  Python → MCP ...
