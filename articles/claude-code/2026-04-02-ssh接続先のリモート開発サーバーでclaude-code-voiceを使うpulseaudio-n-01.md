---
id: "2026-04-02-ssh接続先のリモート開発サーバーでclaude-code-voiceを使うpulseaudio-n-01"
title: "SSH接続先のリモート開発サーバーでClaude Code /voiceを使う（PulseAudio null-sink方式）"
url: "https://zenn.dev/eight8/articles/0714b324a05726"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "VSCode", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

マイクがない
マイクがない。
正確には、マイクはある。目の前のWindowsに繋がったBluetoothイヤホンにマイクはついている。ただ、私が開発しているのはそのWindowsではなく、隣の部屋に置いてあるUbuntuサーバーだ。VSCode Remote SSHで繋いでいる。画面の向こうにいるサーバーには、マイクがない。
Claude Codeに /voice という機能がある。スペースキーを長押しすると声でコードの指示が出せる。キーボードを打つより圧倒的に楽で、一度使うと戻れなくなる類の快適さだった。以前、WSL2で開発していた頃に、PulseAudioの設定や音量調整と格闘し...
