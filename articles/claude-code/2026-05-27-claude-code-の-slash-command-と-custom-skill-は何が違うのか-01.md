---
id: "2026-05-27-claude-code-の-slash-command-と-custom-skill-は何が違うのか-01"
title: "Claude Code の slash command と custom skill は何が違うのか"
url: "https://zenn.dev/gudezou/articles/d3b954f51bca04"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/543cb763f085-20260527.png)

* Claude Code の公式 docs は、custom commands は skills に統合されたと書いています。
* `.claude/commands/foo.md` と `.claude/skills/foo/SKILL.md` はどちらも同じ `/foo` を生み、commands 形式はそのまま動き続けます。
* skill 形式だけが、補助ファイル用のディレクトリ・自動読み込み・paths による絞り込み・呼び出し制御の frontmatter を持ちます。

---

## 公式 docs は commands を skills に統合済みと書いている

Anthropic Docs > Extend Claude with skills のページに「custom commands は skills に統合された」と書かれています。  
同じ `/deploy` という slash 名は、commands 形式のファイル `.claude/commands/deploy.md` からも作れるし  
skill 形式のディレクトリ `.claude/skills/deploy/SKILL.md` からも作れて、両者は同じように動きます。  
既存の `.claude/commands/` のファイルはそのまま動き続け、同じ frontmatter をサポートします。  
Anthropic Docs > Commands ページでも、自分のコマンドを足したい場合は Skills のページを見るよう誘導されています。

![commands と skills の両方から同じ slash 名が生まれる対比図](https://static.zenn.studio/user-upload/0b45239cd60a-20260527.png)

---

## commands には書けない自動 invoke と paths

skill 形式が `.claude/commands/` 形式に対して持っている追加機能は、おもに3つあります。

1つ目は、補助ファイルを置けるディレクトリ構造です。  
`SKILL.md` のとなりに `reference.md` や `examples.md`、`scripts/` などを置けます。  
長い参考資料は本体から切り離しておけて、必要なときだけ参照できます。

2つ目は、ユーザーと Claude のどちらが呼び出すかを制御する frontmatter です。  
デフォルトでは、ユーザーは `/skill-name` と打って直接呼び出せます。  
Claude も、会話に関連すると判断したときに自動で読み込めます。  
ここに `disable-model-invocation: true` を書くと、ユーザーがタイミングを決めて呼び出す形に絞れます。  
`/commit` や `/deploy` のように副作用のあるワークフローで使う想定です。  
逆に `user-invocable: false` を書くと、ユーザーの `/` メニューからは隠れ、Claude だけが背景知識として読み込む形になります。

3つ目は、paths frontmatter による自動起動の絞り込みです。  
glob パターンを書いておくと、そのパターンに合うファイルを扱うときだけ Claude が自動で読み込みます。  
たとえば API クライアントの実装ファイルだけに反応する skill や、特定のドキュメントを編集するときだけ呼ばれる skill を作れます。

Claude が自動で読み込むかどうかは、skill の description フィールドが手がかりになります。  
そのため、自動でも呼ばれたい skill には、ユーザーが自然に書きそうな言葉を description に入れておくのが効きます。  
ただし description と when\_to\_use を合わせた表示は 1536字で打ち切られるので、主用途を先に置く必要があります。  
合わせて、skill 本体は一度読み込まれると以後のターンにわたってコンテキストに残ります。  
本文は簡潔に保ち、長い参考資料は補助ファイルに分けるのが目安です。

なお、Anthropic Docs > Create custom subagents のページに subagent の機能があります。  
subagent は skill とは別のレイヤーで、独自のコンテキストウィンドウと独立した権限を持ちます。  
副タスクで主会話を埋め尽くしたくない場面で、skill と組み合わせて使えます。  
skill 側にも context: fork という frontmatter があり、skill 自身を subagent として走らせる選択肢もあります。

![skill 固有の frontmatter 3つと挙動の対応図](https://static.zenn.studio/user-upload/a9e93bc004cb-20260527.png)

---

## 参考文献

1. Anthropic. *Extend Claude with skills - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/skills>
2. Anthropic. *Commands - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/commands>
3. Anthropic. *Create custom subagents - Claude Code Docs*. Anthropic Documentation. <https://code.claude.com/docs/en/sub-agents>
