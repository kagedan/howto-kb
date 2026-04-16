---
id: "2026-04-15-claude-code-のスラッシュコマンド全部わかるbatch-loop-simplify-など全-01"
title: "Claude Code のスラッシュコマンド全部わかる——/batch /loop /simplify など全16コマンド徹底解説"
url: "https://qiita.com/TaichiEndoh/items/50392c3ccc0e55d9ca8a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code のターミナルで `/` を打つと、ずらっとコマンドが並びます。

```
/batch        /claude-api   /compact      /context
/cost         /debug        /extra-usage  /heapdump
/init         /insights     /loop         /review
/security-review  /simplify  /update-config  /schedule
/clear        /export
```

「なんとなく使ってるけど全部は把握してない」という方向けに、各コマンドの役割・使いどころ・具体例を一本でまとめます。

---

## コマンドの2種類を先に整理する

Claude Code のスラッシュコマンドには、仕組みの異なる2種類があります。

| 種別 | 例 | 仕組み |
|-----|---|------|
| **ビルトインコマンド** | `/clear` `/compact` `/co
