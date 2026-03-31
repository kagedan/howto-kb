---
id: "2026-03-31-raspberry-piでclaude-codeを起動時に自動実行してdiscordボットとして常駐-01"
title: "Raspberry PiでClaude Codeを起動時に自動実行してDiscordボットとして常駐させる"
url: "https://qiita.com/supertask/items/ab017f78d75fb9a1f61b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

  Raspberry Pi を常時稼働サーバーとして使い、PC起動時に Claude Code を自動起動して Discord
  チャンネルに常駐させる方法を紹介します。

  ターミナルウィンドウが画面上に表示されるので、Claude の動作状況をいつでも目視で確認できます。

  ### 環境

  - Raspberry Pi 5 (aarch64)
  - Debian 13 (trixie) / Raspberry Pi OS
  - Claude Code 2.1.x
  - デスクトップ環境 (Wayland / lxterminal)

  ## 前提条件

  - Claude Code がインストール済みで `claude` コマンドが使えること
  - Discord プラグインが設定済みであること
      - [Claude Code を Discord と連携させる公式ボットのセットアップ手順](https://zenn.dev/edom18/articles/claude-code-discord-bot-setup)
  -
