---
id: "2026-03-31-過去の-session-をほしい時に参照する方針で-claude-mem-のトークン消費を激減させた-01"
title: "過去の session をほしい時に参照する方針で claude-mem のトークン消費を激減させた話"
url: "https://qiita.com/nishiken1118/items/6b16557fcabf784c861e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

*最終更新日: 2026-03-22*

# 過去の session をほしい時に参照する方針で claude-mem のトークン消費を激減させた話

[claude-mem](https://github.com/thedotmack/claude-mem) は Claude Code にセッション間の永続メモリを与える便利なツールですが、観測記録が蓄積されるにつれてセッション開始時の自動注入でトークン消費が膨らんでいきます。

この記事では、トークン消費を抑えつつ claude-mem の恩恵を最大限に受けるための設定を、実際の運用をもとに解説します。

---

## 推奨設定の全体像

### 設定の方針

**「事前の自動注入を極限まで絞り、必要な情報は都度取得する」** という方針です。
claude-mem が持つセッション開始時のコンテクスト注入を極限まで絞る代わりに、こちらの指示で明示的に過去の詳細な情報をとってくるようにします。

### settings.json

設定ファイルは `~/.claude-mem/settings.json` にあります。以下が実際
