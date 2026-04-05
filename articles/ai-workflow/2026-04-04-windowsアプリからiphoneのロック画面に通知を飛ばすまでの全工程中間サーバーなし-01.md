---
id: "2026-04-04-windowsアプリからiphoneのロック画面に通知を飛ばすまでの全工程中間サーバーなし-01"
title: "WindowsアプリからiPhoneのロック画面に通知を飛ばすまでの全工程（中間サーバーなし）"
url: "https://zenn.dev/hirobu/articles/e646681739e12b"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

概要
Windowsのデスクトップアプリ（Tauri / Rust）から、iPhoneのロック画面にプッシュ通知を送る仕組みを実装した。
一般的なWeb Pushの実装では、中継サーバー（Node.jsなど）を用意して web-push ライブラリを使うのが定石だが、今回は中間サーバーを一切用意せず、Rustから直接AppleのAPNs（Apple Push Notification service）へ暗号化ペイロードを投げつける構成にした。

運用コスト：維持費 ¥0

自前サーバー：なし（データの保存先はユーザー個人のGoogleドライブのみ）
速度：PCから送信して1秒以内にi...
