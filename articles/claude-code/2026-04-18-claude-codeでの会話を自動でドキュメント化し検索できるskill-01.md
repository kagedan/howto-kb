---
id: "2026-04-18-claude-codeでの会話を自動でドキュメント化し検索できるskill-01"
title: "Claude Codeでの会話を自動でドキュメント化し検索できるskill"
url: "https://qiita.com/dd7223dd/items/ce4ce80aac3b18410a5a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude Codeで日々コードを書いたり調査をしていると、会話の中で生まれる知識が想像以上に多いことに気づきます。

- バグの根本原因と対処法
- 画面操作の手順
- 「この機能は実はこういう仕様だった」という発見
- ドメイン知識

でもこれらは、会話を閉じた瞬間に消えます。メモリーに残るものもありますが、限定的です。かといってAIに要約させて、コピペしてWikiに貼るのは面倒で、結局続きません。

そこで、会話を止めずに「〇〇に保存して」「あの件のドキュメントある？」と言えばClaudeが勝手にやってくれる仕組みを、Claude CodeのSkill機能で作りました。この記事はその設計と、真似して自分で作るためのポイントの解説です。

本記事ではドキュメント管理ツールを「hedgedoc」で説明してますが、ツール自体はAPIで管理できれば、なんでも問題ないです。

# 概要

保存と検索2つのSkillを作りました。

### `/hedgedoc-save` （保存）

```
ユーザー:「/hedgedoc-save」
Claude: 「hedgedoc-
