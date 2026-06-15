---
id: "2026-06-15-aibusiness9-httpstcogck8fl9u0x-01"
title: "@AIbusiness9: https://t.co/GCK8FL9U0X"
url: "https://x.com/AIbusiness9/status/2066316165023232235"
source: "x"
category: "claude-code"
tags: ["claude-code", "OpenAI", "GPT", "x"]
date_published: "2026-06-15"
date_collected: "2026-06-15"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

https://t.co/GCK8FL9U0X


--- Article ---
「AIは補助ツール」で止まってる人、完全に宝の持ち腐れです。Anthropicの中の人(Claude Codeを作った本人)は、自分の業務を完全にAIに任せています。Google・OpenAIなどの会社までにも、人間が働かない働き方の波が来ています。「今後の10年で勝ち残りたい人」は、必ずこの記事を見てください。

その動画はこちら。

https://x.com/0xMovez/status/2051398716553122302

語っているのは、AnthropicのClaude Code開発を率いるBoris Cherny。

「過去2ヶ月、自分のコードは100%AIが書いた」と告白した直後、業界中がザワつきました。

「正直、AI活用の解説本を10冊読むより、この動画1本のほうが価値がある」と言いたくなるレベルの内容。

ここから、AnthropicのClaude Codeを作った本人が何をやっているか、Google・OpenAI・MEDViで起きている同じ現象、そして起業家・フリーランス・個人開発者にとって何が示唆なのかを、順番に解剖していきます。

![](https://pbs.twimg.com/media/HK0GYmDbIAAiD2g.jpg)

## **1. Claude Codeを作った本人が、コードを書いていない**

本題に入る前に、状況を整理しておきます。

Boris Cherny。

Anthropicで Claude Code 開発をリードしている人物です。

![](https://pbs.twimg.com/media/HK0Gap1b0AEW5cS.jpg)

Claude Codeというのは、Anthropicが2025年5月に出した、ターミナルで動くAIコーディング・エージェント。

2025年5月のローンチから6ヶ月で**$1B ARR**を達成しました。ChatGPTより速いスピードで$1Bに到達した史上最速級のプロダクトです。

2026年2月時点では**$2.5B ARR**。

GitHubコミットの**4%**がClaude Codeによるもので、年末には**20%到達**するとSemiAnalysisが予測しています。

つまり、世界中のソフトウェア開発のかなりの割合が、すでにClaude Code経由で動いている。

そのプロダクトの開発をリードしているBoris Cherny本人が、Pragmatic Engineerとのインタビューで、こう告白したわけです。

*Pretty much 100% of their team's code is written by Claude Code and Opus 4.5. For him personally it has been 100% for two+ months, and he shipped 22 PRs yesterday and 27 the day before, each one 100% written by Claude.*

訳すと、こうなる。

「チーム全体のコードはほぼ100% Claude Codeで書かれている。自分個人では2ヶ月以上100% AI作成。昨日は22個のPR、その前の日は27個のPR、すべて100% Claudeが書いた」。

22本のPR、27本のPR。

1日に。

しかも100% AI生成。

普通のエンジニアなら、ちゃんと書いたPRを1日2〜3本出せれば上出来です。

それの**10倍のスピード**で、しかも自分の手を動かしていない。

これがClaude Codeを作った本人の働き方です。

## **2. 「100%AIに任せる」を実装している具体的な仕組み**

「100%AIが書いている」と言われても、実際にどうやってるのかがイメージできない。

そこを噛み砕きます。

BorisのworkflowはVentureBeatとPragmatic Engineerのインタビューで、かなり具体的に公開されています。

まずローカルターミナルで5つのClaude Codeインスタンスを並列実行（タブ#1-5）、claude.aiブラウザで5-10セッションを同時管理。iTerm2のsystem notificationsで「Claudeが入力待機」を通知させて、画面をずっと監視しなくていい状態を作っています。

加えて、3ステップ以上のタスクではPlan Modeを常用して「計画を確認してから実装」をエミュレート。/commit-push-prというSlash Commandで
