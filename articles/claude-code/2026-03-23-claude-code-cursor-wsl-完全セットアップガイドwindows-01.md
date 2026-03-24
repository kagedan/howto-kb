---
id: "2026-03-23-claude-code-cursor-wsl-完全セットアップガイドwindows-01"
title: "Claude Code × Cursor × WSL 完全セットアップガイド（Windows）"
url: "https://qiita.com/LingmuSajun/items/bdcaa74e1cbfa54515a2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

# Claude Code × Cursor × WSL 完全セットアップガイド（Windows）

> **対象**: Windows 10/11 ・ ツール未インストールの状態からスタート
> **ゴール**: WSL + Cursor + Claude Code の本格開発環境を構築し、育てていく

---

## 全体の流れ

```
① WSL（Ubuntu）のインストール & 初期設定
② WSL内に Claude Code をインストール
③ Anthropicアカウント認証（Claude Pro / Max 必須）
④ Cursor インストール & WSL連携
⑤ プロジェクトフォルダの作り方 & claude 起動
⑥ CLAUDE.md で Claude Code を「育てる」
```

---

## ① WSL（Ubuntu）のインストール

### WSLとは？

Windows上でLinux（Ubuntu）を動かすMicrosoft公式の仕組み。
Claude CodeはもともとLinux/macOS向けに設計されているため、
WSL経由が最も安定してパフ
