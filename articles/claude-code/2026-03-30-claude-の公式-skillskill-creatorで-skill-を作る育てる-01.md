---
id: "2026-03-30-claude-の公式-skillskill-creatorで-skill-を作る育てる-01"
title: "Claude の公式 skill「skill-creator」で skill を作る・育てる"
url: "https://qiita.com/s-sakano/items/b8ec3acf55153a252d6e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-03-30"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

こんにちは！

この記事では、Claude の公式 skill「**skill-creator**」で skill を自分で作ったり直したりする方法を紹介します。
伝えたいことは次の3つです。**skill とは何か**、**skill と MCP それぞれの役割は何か**、**skill-creator の入れ方と使い方**です。とくに Claude Code を触り始めたばかりの人や「skill って聞いたことはあるけど中身は知らない」という人がいましたら、最後まで読んでいただけると嬉しいです。

## skill って何？ どう使う？

**skill** は、Claude に「この仕事のときはこの手順を見て動いて」と渡す**指示のまとまり**です。`SKILL.md` というファイルに書いておくと、Claude がそれを参照して動きます。

呼び出し方は次の2つです。**手動**で **`/` を付けて** skill を読み込むか、**会話の内容に合わせて自動**で読み込まれるかです。手動で使う名前は `SKILL.md` の **`name`** に対応します。

---
