---
id: "2026-05-05-l-go-mrk-httpstcow58ihc3d9l-01"
title: "@L_go_mrk: https://t.co/W58ihc3D9l"
url: "https://x.com/L_go_mrk/status/2051588898900586831"
source: "x"
category: "claude-code"
tags: ["claude-code", "OpenAI", "x"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-x"
---

https://t.co/W58ihc3D9l


--- Article ---
こんにちは、AI駆動塾です。

ネットを見ていると、日々さまざまな発信者が「Claude Codeのベストプラクティス」を発信しています。ただ、それらの多くは発信者個人の使い方にカスタマイズされた内容で、必ずしも汎用的とは言いきれません。

そんな中、汎用的に通用する「Claude Codeのベストプラクティス」を見つけました。Anthropic公式が出している内容です。

今回はAnthropicが公開している2つのドキュメント — 「How Anthropic teams use Claude Code」と「Best practices for Claude Code」 — を中心に、Anthropicのエンジニアが社内でClaude Codeをどう使っているのかをまとめました。

===

**＜PR＞engram - 超精密エンジニア診断**

![](https://pbs.twimg.com/media/HHh74A_aIAEjnJG.png)

「**資質**」「**特性**」「**経験**」の3軸 × 各10次元で、エンジニアとしての全体像を可視化する診断サービスです。100問の設問に答えるだけで、自分の個性が立体的に見えるようになります。

診断後は、自分のプロファイルにマッチする**案件オファーが匿名で届く**機能も使えます。今の会社や経歴を晒さずに、市場が自分にいくらの値段をつけるかを観測できる設計です。

👉 https://engram-axg.pages.dev/?utm_source=x&utm_medium=social&utm_campaign=engram_article&utm_content=article-03

===

まず、AnthropicがどれだけClaude Codeを使い倒しているのか、まずいくつか数字を見ておきます。

Anthropicの広報が2026年1月、Fortuneの取材に対してこう発言しています。

> **「社内全体で、コードの70〜90%がClaude Codeで書かれている」**
（出典: [https://fortune.com/2026/01/29/100-percent-of-code-at-anthropic-and-openai-is-now-ai-written-boris-cherny-roon/](https://fortune.com/2026/01/29/100-percent-of-code-at-anthropic-and-openai-is-now-ai-written-boris-cherny-roon/) ）

Claude Codeの開発責任者であるBoris Cherny本人は、もう一段先を行っています。**2025年11月以降、自分のコードを1行も手で書いていない**。毎日10〜30件のPull Requestを出し、その全てがClaude Codeによる生成だと公にしています（出典: [https://www.developing.dev/p/boris-cherny-creator-of-claude-code](https://www.developing.dev/p/boris-cherny-creator-of-claude-code) ）。

会社の規模感も異常です。Anthropicは2025年初頭から従業員数が3倍に増えていますが、**1人あたりのエンジニア生産性は同時期に約70%上昇**しています。組織が3倍に拡張されたとき、普通は1人あたりの生産性が下がります。Anthropicの場合は逆に上がっている。差分の正体がClaude Codeの社内活用です（出典: [https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens) ）。

外側の数字も塗り替わっています。SemiAnalysisが2026年2月に出した分析によると、GitHubの公開コミットの**4%が既にClaude Code製**。同社は「2026年末には20%を超える」と予測しています（出典: [https://newsletter.semianalysis.com/p/claude-code-is-the-inflection-point](https://newsletter.semianalysis.com/p/claude-code
