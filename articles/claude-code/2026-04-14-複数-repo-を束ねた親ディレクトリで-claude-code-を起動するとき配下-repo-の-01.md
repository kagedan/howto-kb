---
id: "2026-04-14-複数-repo-を束ねた親ディレクトリで-claude-code-を起動するとき配下-repo-の-01"
title: "複数 repo を束ねた親ディレクトリで Claude Code を起動するとき、配下 repo の skills も使いたい"
url: "https://zenn.dev/tasteck/articles/3d1f044aeaf491"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

TL;DR
Claude Code の project skills は、普通に各リポジトリの中で運用していると思います。
ただ、自分は複数 repo をまたいで調査することが多く、そういうときは repo ごとに Claude Code を起動するより、関連する repo を束ねた親ディレクトリから起動したくなります。
そのままだと配下 repo の project skills をまとめて扱いにくいので、起動時だけ親ディレクトリ側の .claude/skills に symlink を張るようにしています。

 やりたいこと
イメージとしてはこんな構成です。
workspace/...
